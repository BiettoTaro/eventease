import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from app.main import app
from app.db.database import Base, get_db
from sqlalchemy.orm import sessionmaker

# Use SQLite file for testing to ensure shared database
import tempfile
import os

# Create a temporary file for the test database
temp_db_file = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
temp_db_path = temp_db_file.name
temp_db_file.close()

SQLALCHEMY_DATABASE_URL = f"sqlite:///{temp_db_path}"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create all tables at module level
Base.metadata.create_all(bind=engine)

# Override get_db dependency
def override_get_db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

# Global test database session
_test_db = None

def get_test_db():
    global _test_db
    if _test_db is None:
        Base.metadata.create_all(bind=engine)
        _test_db = TestingSessionLocal()
    try:
        yield _test_db
    finally:
        pass  # Don't close the session here, let the fixture handle it

app.dependency_overrides[get_db] = get_test_db

@pytest.fixture
def test_client():
    """Test client fixture"""
    return TestClient(app)

@pytest.fixture
def db():
    """Database session fixture for testing"""
    global _test_db
    Base.metadata.create_all(bind=engine)
    if _test_db is None:
        _test_db = TestingSessionLocal()
    yield _test_db
