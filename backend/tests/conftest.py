from unittest.mock import patch, Mock

import pytest

from .. import utils
from ..models import UserRead, UserCreate

from sqlmodel import Session, SQLModel, create_engine


@pytest.fixture(scope="class")
def default_user() -> UserRead:
    new_user = UserCreate(
        email="dummy_user@example.com",
        fullname="dummy_user",
        password="calory"
    )
    new_password = utils.get_hashed_password(new_user.password)
    new_user.password = new_password
    return UserRead(**new_user.dict(), id=1)
