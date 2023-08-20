import os

from sqlmodel import SQLModel, create_engine

db_engine_url = os.getenv("DATABASE_URL", "sqlite:///database.db")

engine = create_engine(db_engine_url, echo=False)


# Create database tables
def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def shutdown_db_session():
    engine.dispose()
