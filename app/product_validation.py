from app.models import Product
from app.schemas import ProductInput


def apply_product_input(product: Product, payload: ProductInput) -> Product:
    for key, value in payload.model_dump().items():
        setattr(product, key, value)
    return product
