from tests.helpers import register_and_login


def create_cart(client):
    headers = register_and_login(client)
    products = client.get("/products").json()
    client.post(
        "/cart/items",
        headers=headers,
        json={"product_id": products[0]["id"], "quantity": 2},
    )
    return headers, products[0]


def test_checkout_calculates_total_and_decrements_stock(client):
    headers, product = create_cart(client)
    response = client.post("/orders", headers=headers)
    assert response.status_code == 201
    assert response.json()["total"] == product["price"] * 2
    remaining = next(p for p in client.get("/products").json() if p["id"] == product["id"])
    assert remaining["stock"] == product["stock"] - 2
    assert client.get("/cart", headers=headers).json() == []


def test_checkout_rejects_insufficient_stock(client):
    headers, product = create_cart(client)
    client.post(
        "/cart/items",
        headers=headers,
        json={"product_id": product["id"], "quantity": 100},
    )
    response = client.post("/orders", headers=headers)
    assert response.status_code == 409
    refreshed = next(p for p in client.get("/products").json() if p["id"] == product["id"])
    assert refreshed["stock"] == product["stock"]


def test_order_cancellation_restores_inventory(client):
    headers, product = create_cart(client)
    order = client.post("/orders", headers=headers).json()
    cancelled = client.post(f"/orders/{order['id']}/cancel", headers=headers)
    assert cancelled.status_code == 200
    refreshed = next(p for p in client.get("/products").json() if p["id"] == product["id"])
    assert refreshed["stock"] == product["stock"]
