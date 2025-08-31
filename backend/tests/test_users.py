import pytest 
from datetime import datetime, timedelta, timezone
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.models.user import User
from app.utils.security import get_password_hash, create_access_token
from app.schemas.user import UserCreate


class TestUsers:
    """Test suite for users CRUD operations and password validation"""
    
    def test_create_user_success(self, test_client: TestClient, db: Session):
        """Test successful user creation with valid data"""
        user_data = {
            "email": "test@example.com",
            "name": "Test User",
            "password": "Test123!",
            "latitude": 51.5074,
            "longitude": -0.1278,
            "city": "London",
            "country": "UK"
        }
        
        response = test_client.post(
            "/users/",
            json=user_data
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == user_data["email"]
        assert data["name"] == user_data["name"]
        assert data["latitude"] == user_data["latitude"]
        assert data["longitude"] == user_data["longitude"]
        assert data["city"] == user_data["city"]
        assert data["country"] == user_data["country"]
        assert data["is_admin"] == False  # Default value
        assert "id" in data
        assert "password_hash" not in data  # Password should not be returned
    
    def test_create_user_minimal_data(self, test_client: TestClient, db: Session):
        """Test user creation with only required fields"""
        user_data = {
            "email": "minimal@example.com",
            "name": "Minimal User",
            "password": "Minimal123!"
        }
        
        response = test_client.post(
            "/users/",
            json=user_data
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == user_data["email"]
        assert data["name"] == user_data["name"]
        assert data["latitude"] is None
        assert data["longitude"] is None
        assert data["city"] is None
        assert data["country"] is None
    
    def test_create_user_duplicate_email(self, test_client: TestClient, db: Session):
        """Test user creation fails with duplicate email"""
        # Create first user
        user_data = {
            "email": "duplicate@example.com",
            "name": "First User",
            "password": "First123!"
        }
        
        response = test_client.post("/users/", json=user_data)
        assert response.status_code == 200
        
        # Try to create second user with same email
        duplicate_data = {
            "email": "duplicate@example.com",
            "name": "Second User",
            "password": "Second123!"
        }
        
        response = test_client.post("/users/", json=duplicate_data)
        assert response.status_code == 400  # Should fail due to unique constraint
    
    def test_password_validation_too_short(self, test_client: TestClient, db: Session):
        """Test password validation fails for passwords less than 8 characters"""
        user_data = {
            "email": "short@example.com",
            "name": "Short Password User",
            "password": "Short1"  # Only 7 characters
        }
        
        response = test_client.post("/users/", json=user_data)
        assert response.status_code == 422  # Validation error
        error_detail = response.json()["detail"][0]
        assert "Password must be at least 8 characters long" in error_detail["msg"]
    
    def test_password_validation_no_uppercase(self, test_client: TestClient, db: Session):
        """Test password validation fails for passwords without uppercase letters"""
        user_data = {
            "email": "noupper@example.com",
            "name": "No Uppercase User",
            "password": "nouppercase123!"  # No uppercase letters
        }
        
        response = test_client.post("/users/", json=user_data)
        assert response.status_code == 422  # Validation error
        error_detail = response.json()["detail"][0]
        assert "Password must contain at least one uppercase letter" in error_detail["msg"]
    
    def test_password_validation_no_lowercase(self, test_client: TestClient, db: Session):
        """Test password validation fails for passwords without lowercase letters"""
        user_data = {
            "email": "nolower@example.com",
            "name": "No Lowercase User",
            "password": "NOLOWERCASE123!"  # No lowercase letters
        }
        
        response = test_client.post("/users/", json=user_data)
        assert response.status_code == 422  # Validation error
        error_detail = response.json()["detail"][0]
        assert "Password must contain at least one lowercase letter" in error_detail["msg"]
    
    def test_password_validation_no_digit(self, test_client: TestClient, db: Session):
        """Test password validation fails for passwords without digits"""
        user_data = {
            "email": "nodigit@example.com",
            "name": "No Digit User",
            "password": "NoDigit!"  # No digits
        }
        
        response = test_client.post("/users/", json=user_data)
        assert response.status_code == 422  # Validation error
        error_detail = response.json()["detail"][0]
        assert "Password must contain at least one digit" in error_detail["msg"]
    
    def test_password_validation_no_special_char(self, test_client: TestClient, db: Session):
        """Test password validation fails for passwords without special characters"""
        user_data = {
            "email": "nospecial@example.com",
            "name": "No Special Char User",
            "password": "NoSpecial123"  # No special characters
        }
        
        response = test_client.post("/users/", json=user_data)
        assert response.status_code == 422  # Validation error
        error_detail = response.json()["detail"][0]
        assert "Password must contain at least one special character" in error_detail["msg"]
    
    def test_password_validation_valid_password(self, test_client: TestClient, db: Session):
        """Test password validation passes for valid passwords"""
        valid_passwords = [
            "Valid123!",
            "StrongP@ss1",
            "Complex#Pass2",
            "Secure$Pass3"
        ]
        
        for i, password in enumerate(valid_passwords):
            user_data = {
                "email": f"valid{i}@example.com",
                "name": f"Valid User {i}",
                "password": password
            }
            
            response = test_client.post("/users/", json=user_data)
            assert response.status_code == 200, f"Password '{password}' should be valid"
    
    def test_list_users_success(self, test_client: TestClient, db: Session):
        """Test successful listing of all users"""
        # Create some test users
        user1_data = {
            "email": "list1@example.com",
            "name": "List User 1",
            "password": "List123!"
        }
        user2_data = {
            "email": "list2@example.com",
            "name": "List User 2",
            "password": "List123!"
        }
        
        # Create users
        test_client.post("/users/", json=user1_data)
        test_client.post("/users/", json=user2_data)
        
        # List all users
        response = test_client.get("/users/")
        assert response.status_code == 200
        
        users = response.json()
        assert len(users) >= 2
        
        # Check that passwords are not exposed
        for user in users:
            assert "password_hash" not in user
            assert "password" not in user
    
    def test_get_user_by_id_success(self, test_client: TestClient, db: Session):
        """Test successful retrieval of user by ID"""
        # Create a user
        user_data = {
            "email": "getbyid1@example.com",
            "name": "Get By ID User",
            "password": "Get123!@"
        }
        
        create_response = test_client.post("/users/", json=user_data)
        assert create_response.status_code == 200
        
        user_id = create_response.json()["id"]
        
        # Get user by ID
        response = test_client.get(f"/users/{user_id}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["id"] == user_id
        assert data["email"] == user_data["email"]
        assert data["name"] == user_data["name"]
        assert "password_hash" not in data
    
    def test_get_user_by_id_not_found(self, test_client: TestClient, db: Session):
        """Test user retrieval fails for non-existent user ID"""
        response = test_client.get("/users/999")
        assert response.status_code == 404
        assert "User not found" in response.json()["detail"]
    
    def test_update_user_success(self, test_client: TestClient, db: Session):
        """Test successful user update"""
        # Create a user
        user_data = {
            "email": "update@example.com",
            "name": "Original Name",
            "password": "Update123!"
        }
        
        create_response = test_client.post("/users/", json=user_data)
        assert create_response.status_code == 200
        
        user_id = create_response.json()["id"]
        
        # Update user data
        update_data = {
            "email": "updated@example.com",
            "name": "Updated Name",
            "password": "NewPass123!",
            "latitude": 52.2053,
            "longitude": 0.1218,
            "city": "Cambridge",
            "country": "UK"
        }
        
        response = test_client.put(f"/users/{user_id}", json=update_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["email"] == update_data["email"]
        assert data["name"] == update_data["name"]
        assert data["latitude"] == update_data["latitude"]
        assert data["longitude"] == update_data["longitude"]
        assert data["city"] == update_data["city"]
        assert data["country"] == update_data["country"]
    
    def test_update_user_not_found(self, test_client: TestClient, db: Session):
        """Test user update fails for non-existent user ID"""
        update_data = {
            "email": "nonexistent@example.com",
            "name": "Non-existent User",
            "password": "Pass123!"
        }
        
        response = test_client.put("/users/999", json=update_data)
        assert response.status_code == 404
        assert "User not found" in response.json()["detail"]
    
    def test_update_user_password_validation(self, test_client: TestClient, db: Session):
        """Test password validation during user update"""
        # Create a user
        user_data = {
            "email": "updatepass@example.com",
            "name": "Update Pass User",
            "password": "Valid123!"
        }
        
        create_response = test_client.post("/users/", json=user_data)
        assert create_response.status_code == 200
        
        user_id = create_response.json()["id"]
        
        # Try to update with invalid password
        invalid_update_data = {
            "email": "updatepass@example.com",
            "name": "Update Pass User",
            "password": "weak"  # Invalid password
        }
        
        response = test_client.put(f"/users/{user_id}", json=invalid_update_data)
        assert response.status_code == 422  # Validation error
    
    def test_delete_user_success(self, test_client: TestClient, db: Session):
        """Test successful user deletion"""
        # Create a user
        user_data = {
            "email": "delete@example.com",
            "name": "Delete User",
            "password": "Delete123!"
        }
        
        create_response = test_client.post("/users/", json=user_data)
        assert create_response.status_code == 200
        
        user_id = create_response.json()["id"]
        
        # Delete user
        response = test_client.delete(f"/users/{user_id}")
        assert response.status_code == 200
        assert "User deleted" in response.json()["message"]
        
        # Verify user is deleted
        get_response = test_client.get(f"/users/{user_id}")
        assert get_response.status_code == 404
    
    def test_delete_user_not_found(self, test_client: TestClient, db: Session):
        """Test user deletion fails for non-existent user ID"""
        response = test_client.delete("/users/999")
        assert response.status_code == 404
        assert "User not found" in response.json()["detail"]
    
    def test_user_with_geolocation(self, test_client: TestClient, db: Session):
        """Test user creation and retrieval with geolocation data"""
        user_data = {
            "email": "geo1@example.com",
            "name": "Geo User",
            "password": "Geo123!@",
            "latitude": 40.7128,
            "longitude": -74.0060,
            "city": "New York",
            "country": "USA"
        }
        
        # Create user
        response = test_client.post("/users/", json=user_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["latitude"] == 40.7128
        assert data["longitude"] == -74.0060
        assert data["city"] == "New York"
        assert data["country"] == "USA"
        
        # Retrieve user
        user_id = data["id"]
        get_response = test_client.get(f"/users/{user_id}")
        assert get_response.status_code == 200
        
        retrieved_data = get_response.json()
        assert retrieved_data["latitude"] == 40.7128
        assert retrieved_data["longitude"] == -74.0060
        assert retrieved_data["city"] == "New York"
        assert retrieved_data["country"] == "USA"
    
    def test_user_email_validation(self, test_client: TestClient, db: Session):
        """Test email validation for various email formats"""
        valid_emails = [
            "email1@example.com",
            "email2@domain.co.uk",
            "email3@example.org",
            "email4@numbers.com"
        ]
        
        for i, email in enumerate(valid_emails):
            user_data = {
                "email": email,
                "name": f"Email User {i}",
                "password": "Email123!"
            }
            
            response = test_client.post("/users/", json=user_data)
            assert response.status_code == 200, f"Email '{email}' should be valid"
    
    def test_user_name_validation(self, test_client: TestClient, db: Session):
        """Test name validation for various name formats"""
        valid_names = [
            "John Doe",
            "José María",
            "李小明",
            "O'Connor",
            "123 Numbers",
            "A" * 100  # Long name
        ]
        
        for i, name in enumerate(valid_names):
            user_data = {
                "email": f"name{i}@example.com",
                "name": name,
                "password": "Name123!"
            }
            
            response = test_client.post("/users/", json=user_data)
            assert response.status_code == 200, f"Name '{name}' should be valid"