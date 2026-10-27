from app.formatting import format_money
from app.models import Order


def build_invoice(order: Order) -> dict:
    lines = [
        {
            "description": item.product_name,
            "quantity": item.quantity,
            "unit_price": format_money(item.unit_price),
            "line_total": format_money(item.unit_price * item.quantity),
        }
        for item in order.items
    ]
    return {
        "order_id": order.id,
        "customer_email": order.user.email,
        "status": order.status,
        "lines": lines,
        "total": format_money(order.total),
    }
