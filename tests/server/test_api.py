from fastapi.testclient import TestClient

from trainingsong.server.api import app

client = TestClient(app)


def test_hello():
    response = client.get("/hello")
    assert response.status_code == 200
    assert response.json() == {"hello": "world"}
