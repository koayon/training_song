import pytest
from fastapi.testclient import TestClient
import responses
from training_song.server.api import app, attempt_play

client = TestClient(app)


def test_hello():
    response = client.get("/hello")
    assert response.status_code == 200
    assert response.json() == {"hello": "world"}
