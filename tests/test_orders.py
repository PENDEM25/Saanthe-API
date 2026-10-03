from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def _create_user_vendor_and_product(stock_quantity):
    client.post("/auth/register", json={
        "name": "Order Test Vendor",
        "email": "ordertestvendor@test.com",
        "password": "testpassword123"
    })
    login_response = client.post("/auth/login", json={
        "email": "ordertestvendor@test.com",
        "password": "testpassword123"
    })
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    client.post("/vendor/profile", json={"business_name": "Test Shop"}, headers=headers)

    product_response = client.post("/vendor/products", json={
        "name": "Test Product",
        "description": "A test product",
        "price": 10.00,
        "stock_quantity": stock_quantity
    }, headers=headers)
    product_id = product_response.json()["id"]

    return headers, product_id


def test_create_order_with_sufficient_stock_succeeds():
    headers, product_id = _create_user_vendor_and_product(stock_quantity=5)

    response = client.post("/orders", json={
        "items": [{"product_id": product_id, "quantity": 2}]
    }, headers=headers)

    assert response.status_code == 201
    assert response.json()["status"] == "PENDING"


def test_create_order_with_insufficient_stock_fails_and_does_not_change_stock():
    headers, product_id = _create_user_vendor_and_product(stock_quantity=1)

    response = client.post("/orders", json={
        "items": [{"product_id": product_id, "quantity": 5}]
    }, headers=headers)
    assert response.status_code == 409

    products_response = client.get("/products")
    products = products_response.json()
    test_product = next(p for p in products if p["id"] == product_id)
    assert test_product["stock_quantity"] == 1

