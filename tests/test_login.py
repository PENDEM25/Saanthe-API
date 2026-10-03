from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_login_with_correct_credentials_succeeds():
    client.post("/auth/register", json={
        "name": "Login Test User",
        "email": "logintest1@test.com",
        "password": "correctpassword123"
    })

    response = client.post("/auth/login", json={
        "email": "logintest1@test.com",
        "password": "correctpassword123"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_with_wrong_password_fails():
    client.post("/auth/register", json={
        "name": "Login Test User 2",
        "email": "logintest2@test.com",
        "password": "correctpassword123"
    })

    response = client.post("/auth/login", json={
        "email": "logintest2@test.com",
        "password": "wrongpassword456"
    })
    assert response.status_code == 401

