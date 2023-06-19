import os

import pytest
from dotenv import load_dotenv

from trainingsong.server import db

load_dotenv()


@pytest.skip("Skipping db tests")
def test_tokens():
    # Test storing tokens
    EMAIL = "test@example.com"

    # Setup
    with db.database_session():
        db.delete_tokens(EMAIL)

    ACCESS_TOKEN = "access_token"
    REFRESH_TOKEN = "refresh_token"
    EXPIRES_AT = 1689727126

    with db.database_session():
        db.store_tokens(EMAIL, ACCESS_TOKEN, REFRESH_TOKEN, EXPIRES_AT)

    # Assert tokens were stored
    with db.database_session():
        result = db.get_tokens(EMAIL)
        if result:
            assert result["email"] == EMAIL
            assert result["access_token"] == ACCESS_TOKEN
            assert result["refresh_token"] == REFRESH_TOKEN
            assert result["expires_at"] == EXPIRES_AT
        else:
            assert False

    ###########################################################
    # Test updating tokens
    NEW_ACCESS_TOKEN = "new_access_token"
    NEW_REFRESH_TOKEN = "new_refresh_token"
    NEW_EXPIRES_AT = 689727129

    with db.database_session():
        db.update_tokens(EMAIL, NEW_ACCESS_TOKEN, NEW_REFRESH_TOKEN, NEW_EXPIRES_AT)

    # Assert tokens were updated
    with db.database_session():
        result = db.get_tokens(EMAIL)
        if result:
            assert result["email"] == EMAIL
            assert result["access_token"] == NEW_ACCESS_TOKEN
            assert result["refresh_token"] == NEW_REFRESH_TOKEN
            assert result["expires_at"] == NEW_EXPIRES_AT
        else:
            assert False

    ###########################################################
    # Test deleting tokens

    with db.database_session():
        db.delete_tokens(EMAIL)

    # Assert tokens were deleted
    with db.database_session():
        result = db.get_tokens(EMAIL)
        assert result is None


def test_test():
    assert True
