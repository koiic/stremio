from fastapi import APIRouter, Depends, status, HTTPException
from sqlmodel import Session, select

from database import engine
from exception import BadRequestException
from models import UserCreate, User, UserRead, UserToken, UserLogin
from utils import get_hashed_password, verify_password, create_access_token, JWTBearer, decode_token, log_user_activity

router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)


@router.post("/signup", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate):
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


@router.post("/login", response_model=UserToken)
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
            log_user_activity(None, "Login", str(e))
            raise BadRequestException("Incorrect username or password")
