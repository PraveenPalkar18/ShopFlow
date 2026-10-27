from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.formatting import format_money
from app.models import CartItem, Product, User
from app.schemas import CartInput

router = APIRouter(prefix="/cart", tags=["cart"])


@router.get("")
def get_cart(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    items = db.scalars(
        select(CartItem).where(CartItem.user_id == user.id).order_by(CartItem.id)
    ).all()
    return [
        {
            "product_id": item.product_id,
            "product_name": item.product.name,
            "quantity": item.quantity,
            "unit_price": format_money(item.product.price),
            "line_total": format_money(item.product.price * item.quantity),
        }
        for item in items
    ]


@router.post("/items", status_code=201)
def add_to_cart(
    payload: CartInput,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    product = db.get(Product, payload.product_id)
    if product is None or not product.active:
        raise HTTPException(status_code=404, detail="Product not found")
    item = db.scalar(
        select(CartItem).where(
            CartItem.user_id == user.id, CartItem.product_id == product.id
        )
    )
    if item:
        item.quantity += payload.quantity
    else:
        db.add(CartItem(user_id=user.id, product_id=product.id, quantity=payload.quantity))
    db.commit()
    return {"message": "Item added"}
