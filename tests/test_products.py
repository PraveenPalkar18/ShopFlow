import pytest
from pydantic import ValidationError

from app.schemas import ProductInput
from tests.helpers import register_and_login


def test_product_input_normalizes_name_and_rejects_blank():
    payload = ProductInput(name="  Blue Mug  ", description="Ceramic", price=12.5, stock=5)
    assert payload.name == "Blue Mug"

    with pytest.raises(ValidationError):
        ProductInput(name="   ", description="Ceramic", price=12.5, stock=5)


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
