from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_get_my_profile_without_token_fails():
    response = client.get("/users/me")
    assert response.status_code == 401

