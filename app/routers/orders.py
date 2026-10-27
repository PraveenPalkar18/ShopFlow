from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.formatting import format_money
from app.inventory import reserve_stock, restore_stock
from app.invoices import build_invoice
from app.models import CartItem, Order, OrderItem, Product, User
from app.notifications import send_order_cancellation, send_order_confirmation
from app.payments import charge_mock
from app.pricing import calculate_total
from app.schemas import OrderOutput

router = APIRouter(prefix="/orders", tags=["orders"])


@router.post("", response_model=OrderOutput, status_code=201)
def create_order(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    cart_items = list(
        db.scalars(select(CartItem).where(CartItem.user_id == user.id)).all()
    )
    if not cart_items:
        raise HTTPException(status_code=400, detail="Cart is empty")
    total = calculate_total(cart_items)
    if not charge_mock(total)[0]:
        raise HTTPException(status_code=402, detail="Mock payment declined")
    reserved: list[tuple[int, int]] = []
    for item in cart_items:
        if not reserve_stock(db, item.product_id, item.quantity):
            for product_id, quantity in reserved:
                restore_stock(db, product_id, quantity)
            db.rollback()
            raise HTTPException(status_code=409, detail="Insufficient inventory")
        reserved.append((item.product_id, item.quantity))
    order = Order(user_id=user.id, status="paid", total=total)
    db.add(order)
    db.flush()
    response_items = []
    for item in cart_items:
        product: Product = item.product
        order.items.append(
            OrderItem(
                product_id=product.id,
                product_name=product.name,
                quantity=item.quantity,
                unit_price=product.price,
            )
        )
        response_items.append(
            {
                "product_id": product.id,
                "product_name": product.name,
                "quantity": item.quantity,
                "unit_price": format_money(product.price),
                "line_total": format_money(product.price * item.quantity),
            }
        )
        db.delete(item)
    db.commit()
    db.refresh(order)
    send_order_confirmation(user.email, order.id)
    return {"id": order.id, "status": order.status, "total": order.total, "items": response_items}


@router.get("", response_model=list[OrderOutput])
def list_orders(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    orders = db.scalars(
        select(Order).where(Order.user_id == user.id).order_by(Order.id.desc())
    ).all()
    return [
        {
            "id": order.id,
            "status": order.status,
            "total": order.total,
            "items": [
                {
                    "product_id": item.product_id,
                    "product_name": item.product_name,
                    "quantity": item.quantity,
                    "unit_price": format_money(item.unit_price),
                    "line_total": format_money(item.unit_price * item.quantity),
                }
                for item in order.items
            ],
        }
        for order in orders
    ]


@router.get("/{order_id}/invoice")
def get_invoice(
    order_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    order = db.scalar(select(Order).where(Order.id == order_id, Order.user_id == user.id))
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return build_invoice(order)


@router.post("/{order_id}/cancel")
def cancel_order(
    order_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    order = db.scalar(select(Order).where(Order.id == order_id, Order.user_id == user.id))
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    if order.status != "paid":
        raise HTTPException(status_code=409, detail="Order cannot be cancelled")
    order.status = "cancelled"
    for item in order.items:
        restore_stock(db, item.product_id, item.quantity)
    db.commit()
    send_order_cancellation(user.email, order.id)
    return {"id": order.id, "status": order.status}
