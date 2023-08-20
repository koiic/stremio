from datetime import datetime
from typing import Optional

from pydantic import EmailStr
from sqlmodel import SQLModel, Column, Field, VARCHAR


class UserBase(SQLModel):
    fullname: str
    email: EmailStr = Field(sa_column=Column("email", VARCHAR, unique=True))


class User(UserBase, table=True, extend_existing=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    password: str


class UserCreate(UserBase):
    password: str


class UserRead(UserBase):
    id: int


class UserLogin(SQLModel):
    email: EmailStr
    password: str


class UserToken(SQLModel):
    access_token: str


class ratedMovie(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    userId: int = Field(index=True)
    movieId: str = Field(index=True)
    rating: str
    timestamp: datetime
