from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_paying_twice_does_not_duplicate_payment():
    client.post("/auth/register", json={
        "name": "Idempotency Test User",
        "email": "idempotencytest@test.com",
        "password": "testpassword123"
    })
    login_response = client.post("/auth/login", json={
        "email": "idempotencytest@test.com",
        "password": "testpassword123"
    })
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    client.post("/vendor/profile", json={"business_name": "Idempotency Test Shop"}, headers=headers)

    product_response = client.post("/vendor/products", json={
        "name": "Idempotency Test Product",
        "description": "A test product",
        "price": 10.00,
        "stock_quantity": 5
    }, headers=headers)
    product_id = product_response.json()["id"]

    order_response = client.post("/orders", json={
        "items": [{"product_id": product_id, "quantity": 1}]
    }, headers=headers)
    order_id = order_response.json()["id"]

    first_payment = None
    for _ in range(10):
        response = client.post(f"/orders/{order_id}/pay", headers=headers)
        if response.json()["status"] == "SUCCESS":
            first_payment = response.json()
            break

    assert first_payment is not None, "Payment never succeeded in 10 attempts"

    second_response = client.post(f"/orders/{order_id}/pay", headers=headers)
    second_payment = second_response.json()

    assert second_payment["id"] == first_payment["id"]

