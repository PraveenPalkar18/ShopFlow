from app.models import Product
from tests.helpers import register_and_login


def create_cart(client, quantity=2):
    headers = register_and_login(client)
    products = client.get("/products").json()
    client.post(
        "/cart/items",
        headers=headers,
        json={"product_id": products[0]["id"], "quantity": quantity},
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


def test_cart_and_checkout_format_amounts_to_cents(client, test_session_factory):
    headers, product = create_cart(client)
    with test_session_factory() as db:
        db_product = db.get(Product, product["id"])
        db_product.price = 1.231
        db.commit()

    cart_line = client.get("/cart", headers=headers).json()[0]
    assert cart_line["unit_price"] == 1.23
    assert cart_line["line_total"] == 2.46

    order = client.post("/orders", headers=headers).json()
    assert order["items"][0]["unit_price"] == 1.23
    assert order["items"][0]["line_total"] == 2.46


def test_invoice_includes_customer_and_order_details(client):
    headers, product = create_cart(client)
    order = client.post("/orders", headers=headers).json()

    response = client.get(f"/orders/{order['id']}/invoice", headers=headers)

    assert response.status_code == 200
    assert response.json() == {
        "order_id": order["id"],
        "customer_email": "buyer@example.com",
        "status": "paid",
        "lines": [
            {
                "description": product["name"],
                "quantity": 2,
                "unit_price": product["price"],
                "line_total": product["price"] * 2,
            }
        ],
        "total": order["total"],
    }


def test_order_cancellation_restores_inventory_and_sends_notification(client, caplog):
    headers, product = create_cart(client)
    order = client.post("/orders", headers=headers).json()
    cancelled = client.post(f"/orders/{order['id']}/cancel", headers=headers)
    assert cancelled.status_code == 200
    assert (
        f"notification_simulated event=order_cancellation order_id={order['id']} "
        "recipient=buyer@example.com"
    ) in caplog.text
    refreshed = next(p for p in client.get("/products").json() if p["id"] == product["id"])
    assert refreshed["stock"] == product["stock"]
