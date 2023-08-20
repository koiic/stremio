# create a fastapi app

from fastapi import FastAPI

from endpoints import api

from database import create_db_and_tables

app = FastAPI()

app.include_router(api.router)


@app.on_event("startup")
def on_startup():
    create_db_and_tables()


@app.get("/")
def read_root():
    # return a formatted movies opening page - like welcome to stremio where you can view and rate movies
    return {"message": "Welcome to Stremio where you can view and rate movies"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
