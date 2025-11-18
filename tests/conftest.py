import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app import create_app
from db import Base

@pytest.fixture(scope="function")
def test_app():

    engine = create_engine("sqlite:///:memory:", future=True)

    Base.metadata.create_all(bind=engine)

    app = create_app({"engine": engine})
    app.testing = True

    yield app

@pytest.fixture(scope="function")
def client(test_app):
    return test_app.test_client(), test_app

