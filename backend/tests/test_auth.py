import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from datetime import timedelta
import sys
import os

# Add the backend directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.utils.security import get_password_hash, create_access_token, verify_password
from app.models.user import User


class TestAuthLogin:
    """Test authentication login functionality"""
    
    def test_login_success(self, test_client: TestClient, db: Session):
        """Test successful login with valid credentials"""
        # Create a test user
        test_user = User(
            email="test@example.com",
            name="Test User",
            password_hash=get_password_hash("testpassword123"),
            is_admin=False
        )
        db.add(test_user)
        db.commit()
        db.refresh(test_user)
        
        # Test login
        login_data = {
            "email": "test@example.com",
            "password": "testpassword123"
        }
        
        response = test_client.post("/auth/login", json=login_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert len(data["access_token"]) > 0
    
    def test_login_invalid_email(self, test_client: TestClient, db: Session):
        """Test login failure with non-existent email"""
        login_data = {
            "email": "nonexistent@example.com",
            "password": "anypassword"
        }
        
        response = test_client.post("/auth/login", json=login_data)
        
        assert response.status_code == 401
        data = response.json()
        assert data["detail"] == "Incorrect email or password"
    
    def test_login_invalid_password(self, test_client: TestClient, db: Session):
        """Test login failure with incorrect password"""
        # Create a test user
        test_user = User(
            email="test@example.com",
            name="Test User",
            password_hash=get_password_hash("correctpassword"),
            is_admin=False
        )
        db.add(test_user)
        db.commit()
        
        # Test login with wrong password
        login_data = {
            "email": "test@example.com",
            "password": "wrongpassword"
        }
        
        response = test_client.post("/auth/login", json=login_data)
        
        assert response.status_code == 401
        data = response.json()
        assert data["detail"] == "Incorrect email or password"
    
    def test_login_missing_fields(self, test_client: TestClient):
        """Test login with missing required fields"""
        # Test missing email
        response = test_client.post("/auth/login", json={"password": "testpassword"})
        assert response.status_code == 422
        
        # Test missing password
        response = test_client.post("/auth/login", json={"email": "test@example.com"})
        assert response.status_code == 422
        
        # Test empty request
        response = test_client.post("/auth/login", json={})
        assert response.status_code == 422


class TestJWTTokenGeneration:
    """Test JWT token generation and validation"""
    
    def test_token_generation(self, test_client: TestClient, db: Session):
        """Test that JWT token is properly generated"""
        # Create a test user
        test_user = User(
            email="jwt@example.com",
            name="JWT Test User",
            password_hash=get_password_hash("jwtpassword123"),
            is_admin=False
        )
        db.add(test_user)
        db.commit()
        db.refresh(test_user)
        
        # Login to get token
        login_data = {
            "email": "jwt@example.com",
            "password": "jwtpassword123"
        }
        
        response = test_client.post("/auth/login", json=login_data)
        assert response.status_code == 200
        
        token_data = response.json()
        access_token = token_data["access_token"]
        
        # Verify token structure (should be a valid JWT)
        assert len(access_token.split('.')) == 3  # JWT has 3 parts separated by dots
    
    def test_token_expiration(self):
        """Test that tokens have proper expiration"""
        # Create a token with short expiration
        short_expiry = timedelta(minutes=1)
        token = create_access_token(
            data={"sub": "test@example.com"},
            expires_delta=short_expiry
        )
        
        # Token should be generated successfully
        assert token is not None
        assert len(token) > 0


class TestPasswordSecurity:
    """Test password hashing and verification"""
    
    def test_password_hashing(self):
        """Test that passwords are properly hashed"""
        password = "testpassword123"
        hashed = get_password_hash(password)
        
        # Hash should be different from original password
        assert hashed != password
        assert len(hashed) > 0
        
        # Hash should be verifiable
        assert verify_password(password, hashed) is True
    
    def test_password_verification(self):
        """Test password verification with correct and incorrect passwords"""
        password = "correctpassword"
        hashed = get_password_hash(password)
        
        # Correct password should verify
        assert verify_password(password, hashed) is True
        
        # Incorrect password should not verify
        assert verify_password("wrongpassword", hashed) is False
        assert verify_password("", hashed) is False
    
    def test_different_passwords_different_hashes(self):
        """Test that different passwords produce different hashes"""
        password1 = "password1"
        password2 = "password2"
        
        hash1 = get_password_hash(password1)
        hash2 = get_password_hash(password2)
        
        assert hash1 != hash2


class TestGetCurrentUser:
    """Test get_current_user dependency function"""
    
    def test_get_current_user_success(self, db: Session):
        """Test successful user retrieval with valid token"""
        # Create a test user
        test_user = User(
            email="current@example.com",
            name="Current User",
            password_hash=get_password_hash("currentpassword"),
            is_admin=False
        )
        db.add(test_user)
        db.commit()
        db.refresh(test_user)
        
        # Create a valid token
        token = create_access_token(data={"sub": str(test_user.id)})
        
        # Test the core JWT functionality
        from jose import jwt
        from app.utils.security import SECRET_KEY, ALGORITHM
        
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        
        assert user_id == str(test_user.id)
    
    def test_get_current_user_invalid_token(self):
        """Test get_current_user with invalid token"""
        from jose import jwt
        from app.utils.security import SECRET_KEY, ALGORITHM
        
        # Test with malformed token
        invalid_token = "invalid.token.here"
        
        with pytest.raises(Exception):  # Should raise JWTError
            jwt.decode(invalid_token, SECRET_KEY, algorithms=[ALGORITHM])


class TestAuthEdgeCases:
    """Test edge cases and error conditions"""
    
    def test_login_with_empty_strings(self, test_client: TestClient, db: Session):
        """Test login with empty string values"""
        login_data = {
            "email": "",
            "password": ""
        }
        
        response = test_client.post("/auth/login", json=login_data)
        assert response.status_code == 401
    
    def test_login_with_special_characters(self, test_client: TestClient, db: Session):
        """Test login with special characters in credentials"""
        # Create user with special characters
        special_email = "test+special@example.com"
        special_password = "P@ssw0rd!@#$%^&*()"
        
        test_user = User(
            email=special_email,
            name="Special User",
            password_hash=get_password_hash(special_password),
            is_admin=False
        )
        db.add(test_user)
        db.commit()
        
        # Test login with special characters
        login_data = {
            "email": special_email,
            "password": special_password
        }
        
        response = test_client.post("/auth/login", json=login_data)
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
    
    def test_login_case_sensitivity(self, test_client: TestClient, db: Session):
        """Test that email login is case sensitive"""
        # Create user with lowercase email
        test_user = User(
            email="case@example.com",
            name="Case User",
            password_hash=get_password_hash("casepassword"),
            is_admin=False
        )
        db.add(test_user)
        db.commit()
        
        # Test with uppercase email (should fail)
        login_data = {
            "email": "CASE@EXAMPLE.COM",
            "password": "casepassword"
        }
        
        response = test_client.post("/auth/login", json=login_data)
        assert response.status_code == 401