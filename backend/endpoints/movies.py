import os
from datetime import datetime

import requests
from cachetools import TTLCache
from fastapi import Depends, Query, APIRouter, HTTPException
from requests.adapters import HTTPAdapter, Retry
from sqlalchemy.orm import load_only
from sqlmodel import Session, select

import sys

sys.path.append("..")

from backend.database import engine
from backend.exception import BadRequestException
from backend.models import ratedMovie, User
from backend.utils import log_user_activity, JWTBearer, decode_token

router = APIRouter(
    prefix="/movies",
    tags=["movies"],
    responses={404: {"description": "Not found"}},
)

# Initialize a cache
movie_cache = TTLCache(maxsize=200, ttl=3600)  # Cache for 1 hour

MAX_RETRIES = 3
MAX_RETRY_BACKOFF_FACTOR = 1
ERROR_CODES = [500, 502, 403, 400, 401, 404]


def get_current_user(token: str = Depends(JWTBearer())):
    try:
        payload = decode_token(token, os.getenv("JWT_SECRET_KEY"), os.getenv("JWT_ALGORITHM"))
        user_email = payload.get("sub")
        with Session(engine) as session:
            db_user = session.exec(select(User).where(User.email == user_email)).first()
            if not db_user:
                raise HTTPException(status_code=403, detail="Invalid authentication credentials")
            return db_user
    except Exception as e:
        raise HTTPException(status_code=403, detail="Invalid authentication credentials")


def fetch_movies_from_api(offset, limit, query=""):
    base_url = os.getenv("MOVIE_API_URL")
    url = f"{base_url}/?skip={offset}&limit={limit}&query={query}"
    retries = Retry(total=MAX_RETRIES, backoff_factor=MAX_RETRY_BACKOFF_FACTOR, status_forcelist=ERROR_CODES)
    with requests.Session() as session:
        session.mount(base_url, HTTPAdapter(max_retries=retries))
        response = session.get(url)
        return response.json()


def get_movie_data():
    if "movie_data" not in movie_cache:
        movie_cache["movie_data"] = fetch_movies_from_api(0, 100)  # after 1 hour, the cache will be cleared
    return movie_cache["movie_data"]


# fetch movies list
@router.post("/")
def list_movies(search: str = "", offset: int = 0,
                limit: int = Query(default=20, lte=100), current_user: User = Depends(get_current_user)):
    with Session(engine) as session:
        rated_movies = session.exec(select(ratedMovie).where(
            ratedMovie.userId == current_user.id).options(
            load_only("movieId", "rating"))).all()

    # Get movie data from the external API
    movie_data = get_movie_data()

    movies = [
        {**movie, "rating": next((rm.rating for rm in rated_movies if rm.movieId == movie['id']), None)}
        for movie in movie_data['items']
        if not search or search.lower() in movie['title'].lower()
    ]
    # Log user activity
    log_user_activity(current_user.id, "List", "fetch movies list")
    total_movies = movie_data['total']
    movies = movies[offset:offset + limit]

    return {
        "movies": movies,
        "total": total_movies
    }


@router.post("/{movie_id}/vote")
def vote_movie(movie_id: str, vote: int = Query(default=1, gt=-2, lt=2),
               current_user: User = Depends(get_current_user)):
    if vote == 1:
        vote = "upvote"
    elif vote == -1:
        vote = "downvote"
    else:
        raise BadRequestException("Invalid vote value")
        # Log user activity
    log_user_activity(current_user.id, "Vote", f"Movie ID: {movie_id}, Vote: {vote}")
    movies = get_movie_data()['items']
    for movie in movies:
        if movie['id'] == movie_id:
            with Session(engine) as session:
                db_movie = session.exec(select(ratedMovie).where(ratedMovie.movieId == movie_id,
                                                                 ratedMovie.userId == current_user.id)).first()
                if db_movie:
                    # update the vote
                    db_movie.rating = vote

                else:
                    # create a new entry
                    db_movie = ratedMovie(userId=current_user.id, movieId=movie_id, rating=vote,
                                          timestamp=datetime.utcnow())
                session.add(db_movie)
                session.commit()
                session.refresh(db_movie)

            return {
                "message": f"Successfully {vote}d movie : {movie['title']}"
            }
    raise BadRequestException("Movie not found")
