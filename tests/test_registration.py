from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_register_new_user_succeeds():
    response = client.post("/auth/register", json={
        "name": "Test User",
        "email": "testuser1@test.com",
        "password": "testpassword123"
    })
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "testuser1@test.com"
    assert "password" not in data
    assert "password_hash" not in data


def test_register_duplicate_email_fails():
    client.post("/auth/register", json={
        "name": "Test User",
        "email": "testuser2@test.com",
        "password": "testpassword123"
    })

    response = client.post("/auth/register", json={
        "name": "Another User",
        "email": "testuser2@test.com",
        "password": "differentpassword456"
    })
    assert response.status_code == 409

