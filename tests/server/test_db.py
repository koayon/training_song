import asyncio
import json
from unittest.mock import AsyncMock, MagicMock

import pytest
import responses
from dotenv import load_dotenv

from trainingsong.server import db

load_dotenv()

# @responses.activate
# @pytest.mark.asyncio
# async def test_get_tokens():
#     test_request_payload = "test123@gmail.com"
#     test_response_payload = {
#         "email": "test123@gmail.com",
#         "access_token": "foo",
#         "refresh_token": "bar",
#         "expires_at": 42,
#     }

#     responses.add(
#         responses.GET,
#         "https://training-song-api-koayon.vercel.app",
#         json=test_response_payload,
#         status=200,
#     )

#     db.database.fetch_one = AsyncMock(return_value=test_response_payload)
#     response = await db.get_tokens(test_request_payload)

#     assert response == test_response_payload
#     db.database.fetch_one.assert_called_once()


@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    db.create()
    yield


def test_store_tokens(setup_test_db):
    email = "test@example.com"
    access_token = "access_token"
    refresh_token = "refresh_token"
    expires_at = 1689727126

    with db.database_session():
        db.store_tokens(email, access_token, refresh_token, expires_at)

    # Assert tokens were stored
    with db.database_session():
        result = db.get_tokens(email)
        if result:
            assert result["email"] == email
            assert result["access_token"] == access_token
            assert result["refresh_token"] == refresh_token
            assert result["expires_at"] == expires_at
        else:
            assert False


def test_update_tokens(setup_test_db):
    email = "test@example.com"
    access_token = "new_access_token"
    refresh_token = "new_refresh_token"
    expires_at = 689727126

    with db.database_session():
        db.update_tokens(email, access_token, refresh_token, expires_at)

    # Assert tokens were updated
    with db.database_session():
        result = db.get_tokens(email)
        if result:
            assert result["email"] == email
            assert result["access_token"] == access_token
            assert result["refresh_token"] == refresh_token
            assert result["expires_at"] == expires_at
        else:
            assert False


def test_delete_tokens(setup_test_db):
    email = "test@example.com"

    with db.database_session():
        db.delete_tokens(email)

    # Assert tokens were deleted
    with db.database_session():
        result = db.get_tokens(email)
        assert result is None
