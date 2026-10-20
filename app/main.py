import logging

from fastapi import FastAPI

from app.config import settings
from app.database import Base, SessionLocal, engine
from app.models import Product, User
from app.routers import auth, cart, orders, products
from app.security import hash_password

logging.basicConfig(
    level=getattr(logging, settings.log_level, logging.INFO),
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)

app = FastAPI(title="ShopFlow Order Management API", version="1.0.0")
app.include_router(auth.router)
app.include_router(products.router)
app.include_router(cart.router)
app.include_router(orders.router)


@app.on_event("startup")
def initialize_database():
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        if db.query(User).filter_by(email="admin@shopflow.test").first() is None:
            db.add(
                User(
                    email="admin@shopflow.test",
                    password_hash=hash_password(settings.admin_password),
                    is_admin=True,
                )
            )
        if db.query(Product).count() == 0:
            db.add_all(
                [
                    Product(name="Canvas Tote", description="Reusable cotton tote", price=18.50, stock=20),
                    Product(name="Desk Lamp", description="Warm LED desk lamp", price=42.00, stock=8),
                ]
            )
        db.commit()


@app.get("/health")
def health():
    return {"status": "ok"}
