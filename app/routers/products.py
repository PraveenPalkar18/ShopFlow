from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth import require_admin
from app.database import get_db
from app.models import Product, User
from app.product_validation import apply_product_input
from app.schemas import ProductInput, ProductOutput

router = APIRouter(prefix="/products", tags=["products"])


@router.get("", response_model=list[ProductOutput])
def search_products(q: str = "", db: Session = Depends(get_db)):
    statement = select(Product).where(Product.active.is_(True))
    if q:
        statement = statement.where(Product.name.ilike(f"%{q}%"))
    return list(db.scalars(statement.order_by(Product.id)))


@router.post("", response_model=ProductOutput, status_code=201)
def create_product(
    payload: ProductInput,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
):
    product = apply_product_input(Product(), payload)
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


@router.put("/{product_id}", response_model=ProductOutput)
def update_product(
    product_id: int,
    payload: ProductInput,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
):
    product = db.get(Product, product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    apply_product_input(product, payload)
    db.commit()
    db.refresh(product)
    return product
