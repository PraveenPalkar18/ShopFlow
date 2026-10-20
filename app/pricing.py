from decimal import Decimal

from app.formatting import format_money
from app.models import CartItem


def money(value: float | Decimal) -> float:
    return format_money(value)


def calculate_total(items: list[CartItem]) -> float:
    return money(sum((Decimal(str(item.product.price)) * item.quantity for item in items), Decimal(0)))
