import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from app.models import Product


@pytest.fixture()
def test_session_factory():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSession = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    Base.metadata.create_all(engine)
    with TestingSession() as db:
        db.add_all(
            [
                Product(name="Canvas Tote", description="Reusable cotton tote", price=18.50, stock=20),
                Product(name="Desk Lamp", description="Warm LED desk lamp", price=42.00, stock=8),
            ]
        )
        db.commit()
    yield TestingSession
    Base.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture()
def client(test_session_factory):
    def override_get_db():
        with test_session_factory() as db:
            yield db

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
