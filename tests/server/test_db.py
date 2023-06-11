import json
import responses

import pytest
from unittest.mock import AsyncMock, MagicMock

from trainingsong.server.db import (
    get_tokens,
    store_tokens,
    update_tokens,
    delete_tokens,
    database,
)


@responses.activate
@pytest.mark.asyncio
async def test_get_tokens():
    test_request_payload = "test123@gmail.com"
    test_response_payload = {
        "email": "test123@gmail.com",
        "access_token": "foo",
        "refresh_token": "bar",
        "expires_at": 42,
    }

    responses.add(
        responses.GET,
        "https://training-song-api-koayon.vercel.app",
        json=test_response_payload,
        status=200,
    )

    # Mock the database object and its fetch_one method
    database_mock = MagicMock()
    database.fetch_one = AsyncMock(return_value=test_response_payload)

    # Call the function with the test inputs
    response = await get_tokens(test_request_payload)

    # Verify the function returned the expected result
    assert response == test_response_payload

    # Verify fetch_one was called with the expected query
    database.fetch_one.assert_called_once()
