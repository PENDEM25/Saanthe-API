from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def _register_login_vendor_and_product(email_suffix, stock_quantity):
    email = f"authtest{email_suffix}@test.com"
    client.post("/auth/register", json={
        "name": "Auth Test User",
        "email": email,
        "password": "testpassword123"
    })
    login_response = client.post("/auth/login", json={
        "email": email,
        "password": "testpassword123"
    })
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    client.post("/vendor/profile", json={"business_name": "Auth Test Shop"}, headers=headers)

    product_response = client.post("/vendor/products", json={
        "name": "Auth Test Product",
        "description": "A test product",
        "price": 10.00,
        "stock_quantity": stock_quantity
    }, headers=headers)
    product_id = product_response.json()["id"]

    return headers, product_id


def test_cannot_cancel_another_users_order():
    user_a_headers, product_id = _register_login_vendor_and_product("usera", stock_quantity=5)

    order_response = client.post("/orders", json={
        "items": [{"product_id": product_id, "quantity": 1}]
    }, headers=user_a_headers)
    order_id = order_response.json()["id"]

    user_b_headers, _ = _register_login_vendor_and_product("userb", stock_quantity=5)

    response = client.patch(f"/orders/{order_id}/cancel", headers=user_b_headers)
    assert response.status_code == 403

