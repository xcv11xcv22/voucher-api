import os
os.environ["DATABASE_URL"] = "sqlite:///:memory:"
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app import create_app
from db import Base, engine


@pytest.fixture(scope="function")
def test_app():
    app = create_app()
    app.testing = True

    yield app

@pytest.fixture(scope="function")
def client(test_app, setup_db):
    return test_app.test_client(), test_app



@pytest.fixture(scope="function")
def setup_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)