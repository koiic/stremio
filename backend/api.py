from datetime import datetime

import requests
from fastapi import APIRouter, Depends, status, Query, HTTPException
from sqlmodel import Session, select

from database import engine
from exception import BadRequestException
from models import UserCreate, User, UserRead, UserToken, UserLogin, ratedMovie
from utils import get_hashed_password, verify_password, create_access_token, JWTBearer, decode_token
from cachetools import TTLCache
from sqlalchemy.orm import load_only

from requests.adapters import HTTPAdapter, Retry

router = APIRouter()


@router.post("/user/signup", tags=["user"], response_model=UserRead, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate):
    print(user.password, "---")

    with Session(engine) as session:
        db_user = session.exec(select(User).where(User.email == user.email)).first()
        if db_user:
            raise BadRequestException("User already exists")
        user.password = get_hashed_password(user.password)
        db_user = User.from_orm(user)
        session.add(db_user)
        session.commit()
        session.refresh(db_user)
        return db_user


@router.post("/user/login", tags=["user"], response_model=UserToken)
def login(data: UserLogin):
    with Session(engine) as session:
        try:
            db_user = session.exec(select(User).where(User.email == data.email)).first()
            if not db_user:
                raise BadRequestException("Incorrect username or password")
            if not verify_password(data.password, db_user.password):
                raise BadRequestException("Incorrect username or password")
            return create_access_token(db_user.email)
        except Exception as e:
            print(e)
            raise BadRequestException("Incorrect username or password")


# get current user
def get_current_user(token: str = Depends(JWTBearer())):
    try:
        payload = decode_token(token)
        user_email = payload.get("sub")
        with Session(engine) as session:
            db_user = session.exec(select(User).where(User.email == user_email)).first()
            if not db_user:
                raise HTTPException(status_code=403, detail="Invalid authentication credentials")
            return db_user
    except Exception as e:
        print(e)
        raise HTTPException(status_code=403, detail="Invalid authentication credentials")


# Initialize a cache
movie_cache = TTLCache(maxsize=100, ttl=3600)  # Cache for 1 hour

MAX_RETRIES = 3
MAX_RETRY_BACKOFF_FACTOR = 1
ERROR_CODES = [500, 502, 403, 400, 401]


def fetch_movies_from_api(offset, limit, query=""):
    base_url = f"https://august12-uqf7jaf6ua-ew.a.run.app/movies/?skip={offset}&limit={limit}&query={query}"
    # retry 3 times
    retries = Retry(total=MAX_RETRIES, backoff_factor=MAX_RETRY_BACKOFF_FACTOR, status_forcelist=ERROR_CODES)
    with requests.Session() as session:
        session.mount(base_url, HTTPAdapter(max_retries=retries))
        response = session.get(base_url)
        return response.json()


def get_movie_data():
    if "movie_data" not in movie_cache:
        movie_cache["movie_data"] = fetch_movies_from_api(0, 100)  # after 1 hour, the cache will be cleared
    return movie_cache["movie_data"]


# fetch movies list
@router.post("/movies", tags=["movies"])
def list_movies(search: str = "", offset: int = 0,
                limit: int = Query(default=20, lte=100), current_user: User = Depends(get_current_user)):
    # get the upvoted and downvoted movies from the database
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

    total_movies = movie_data['total']
    movies = movies[offset:offset + limit]

    return {
        "movies": movies,
        "total": total_movies
    }


@router.post("/movies/{movie_id}/vote", tags=["movies"])
def vote_movie(movie_id: str, vote: int = Query(default=1, gt=-2, lt=2),
               current_user: User = Depends(get_current_user)):
    if vote == 1:
        vote = "upvote"
    elif vote == -1:
        vote = "downvote"
    else:
        raise BadRequestException("Invalid vote value")
    movie_data = get_movie_data()
    movies = movie_data['items']
    for movie in movies:
        if movie['id'] == movie_id:
            with Session(engine) as session:
                db_movie = session.exec(select(ratedMovie).where(ratedMovie.movieId == movie_id,
                                                                 ratedMovie.userId == current_user.id)).first()
                if db_movie:
                    # update the vote
                    db_movie.rating = vote
                    session.add(db_movie)
                    session.commit()
                    session.refresh(db_movie)

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
