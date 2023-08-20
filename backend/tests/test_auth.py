import os

import pytest
from .. import utils as auth_util

@pytest.mark.usefixtures('default_user')
class TestAuthenticate:

    def test_create_access_token_for_user(self, auth_obj, default_user):
        token = auth_util.create_access_token(default_user.email)['access_token']
        decoded = auth_util.decode_token(token, os.getenv('JWT_SECRET_KEY'), os.getenv('JWT_ALGORITHM'))
        assert isinstance(decoded, dict)
        assert decoded['sub'] == default_user.email
