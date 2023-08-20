import os

import pytest
from dotenv import load_dotenv
from .. import utils as auth_util

load_dotenv()


@pytest.mark.usefixtures('default_user')
class TestAuthenticate:

    def test_create_salt_and_hashed_password(self):
        test_password = "calorry"
        first_password = auth_util.get_hashed_password(test_password)
        second_password = auth_util.get_hashed_password(test_password)

        assert first_password is not second_password

    def test_create_access_token_for_user(self, default_user):
        token = auth_util.create_access_token(default_user.email)['access_token']
        decoded = auth_util.decode_token(token, os.getenv('JWT_SECRET_KEY'), os.getenv('JWT_ALGORITHM'))
        assert isinstance(decoded, dict)
        assert decoded['sub'] == default_user.email

    def test_create_access_token_for_user_wrong_secret_key(self, default_user):
        token = auth_util.create_access_token(default_user.email)['access_token']
        decoded_token = auth_util.decode_token(token, os.getenv('JWT_SECRET_KEY'), algorithms='HMAC')

        assert decoded_token == {}

    def test_create_access_token_for_user_wrong_algo(self, default_user):
        token = auth_util.create_access_token(default_user.email)['access_token']

        decoded_token = auth_util.decode_token(token, os.getenv('JWT_SECRET_KEY'), algorithms='HMAC')

        assert decoded_token == {}
