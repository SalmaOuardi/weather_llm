import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.db import reset_all_tables

@pytest.fixture(autouse=True)
def clean_db():
    reset_all_tables()
    yield
    reset_all_tables()

@pytest.fixture
def client():
    return TestClient(app)
