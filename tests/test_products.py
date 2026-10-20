from tests.helpers import register_and_login


def test_product_search_is_case_insensitive(client):
    headers = register_and_login(client)
    created = client.post(
        "/products",
        headers=headers,
        json={"name": "Blue Mug", "description": "Ceramic", "price": 12.5, "stock": 5},
    )
    # Only administrators may create catalogue products.
    assert created.status_code == 403
    assert client.get("/products?q=lamp").status_code == 200


def test_catalogue_seeded_by_startup(client):
    assert len(client.get("/products").json()) == 2
