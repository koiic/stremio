from unittest.mock import patch, Mock

import pytest

from .. import utils
from ..database import engine
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


@pytest.fixture(autouse=True)
def override_get_db():
    with Session(engine) as session:
        yield session


@pytest.fixture(scope="module")
def test_client():
    return TestClient(app, base_url="http://testserver")

@pytest.fixture(autouse=True)
def mock_external_api(mocker):
    # Mock the requests.get function globally for all tests
    with patch("requests.get") as mock_get:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [{"id": 1, "title": "Movie 1"}, {"id": 2, "title": "Movie 2"}]
        mock_get.return_value = mock_response
        yield mock_response
