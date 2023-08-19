# create a fastapi app

from fastapi import FastAPI

from api import router as api_router
from exception import NotFoundException, BadRequestException, UnauthorizedException
from database import create_db_and_tables

app = FastAPI()


@app.on_event("startup")
def on_startup():
    create_db_and_tables()


@app.get("/")
def read_root():
    # return a formatted movies opening page - like welcome to stremio where you can view and rate movies
    return {"message": "Welcome to Stremio where you can view and rate movies"}




app.include_router(api_router, prefix="/api/v1")

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
