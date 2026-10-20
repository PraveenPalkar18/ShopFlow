from sqlalchemy import update
from sqlalchemy.orm import Session

from app.models import Product


def reserve_stock(db: Session, product_id: int, quantity: int) -> bool:
    result = db.execute(
        update(Product)
        .where(Product.id == product_id, Product.active.is_(True), Product.stock >= quantity)
        .values(stock=Product.stock - quantity)
    )
    return result.rowcount == 1


def restore_stock(db: Session, product_id: int, quantity: int) -> None:
    db.execute(
        update(Product)
        .where(Product.id == product_id)
        .values(stock=Product.stock + quantity)
    )
