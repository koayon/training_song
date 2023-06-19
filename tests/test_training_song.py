import pytest
import responses
from fastapi.testclient import TestClient

from trainingsong.core import _is_valid_email, _training_song, local_app
from trainingsong.ts_utils import URL

client = TestClient(local_app)


def test_test():
    assert 1 == 1


def test_is_valid_email():
    assert _is_valid_email("user@example.com")
    assert not _is_valid_email("user_at_example_dot_com")


@responses.activate
def test_training_song():
    responses.add(
        responses.GET,
        URL,
        json={"song_info": "mock song info"},
        status=200,
    )

    acc, response = _training_song(0.9, verbose=False)

    assert acc == 0.9
    assert "song_info" in response
    assert response["song_info"] == "mock song info"


def test_spotify_callback():
    response = client.get("/local_callback", params={"code": "12345"})
    assert response.status_code == 200
    assert response.text == '"Success! You can close this window."'
