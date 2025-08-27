import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from app.main import app
from app.db.database import Base, get_db
from sqlalchemy.orm import sessionmaker

# Use SQLite in memory for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Override get_db dependency
def override_get_db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture
def test_client():
    return TestClient(app)
        

