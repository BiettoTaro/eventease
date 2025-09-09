import pytest
import sys
import os
import warnings

# Suppress deprecation warnings
warnings.filterwarnings("ignore", category=DeprecationWarning, module="pydantic.*")
warnings.filterwarnings("ignore", category=UserWarning, module="pydantic.*")
warnings.filterwarnings("ignore", category=DeprecationWarning, module="passlib.*")

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
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

# Override get_db dependency
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture
def test_client():
    """Test client fixture"""
    return TestClient(app)

@pytest.fixture(scope="function")
def db():
    """Database session fixture for testing"""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)