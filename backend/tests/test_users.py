"""
User Management Test Suite

This module contains comprehensive tests for the user management system,
covering all CRUD operations, password validation, geolocation handling,
and edge cases for the EventEase application.

Test Coverage:
- User creation with various data combinations
- Password strength validation (length, complexity, character types)
- User retrieval by ID and listing
- User update operations with validation
- User deletion and cleanup
- Geolocation data handling (latitude, longitude, city, country)
- Email and name format validation
- Duplicate email prevention
- Error handling and validation responses

Dependencies:
- pytest: Testing framework
- FastAPI TestClient: HTTP client for testing
- SQLAlchemy: Database ORM
- Custom fixtures: Database session and test client setup

Test Categories:
1. User Creation Tests (5 tests)
2. Password Validation Tests (5 tests)
3. User Retrieval Tests (2 tests)
4. User Update Tests (3 tests)
5. User Deletion Tests (2 tests)
6. Geolocation Tests (1 test)
7. Validation Tests (2 tests)

Total Tests: 20
"""

import pytest 
from datetime import datetime, timedelta, timezone
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.models.user import User
from app.utils.security import get_password_hash, create_access_token
from app.schemas.user import UserCreate


class TestUsers:
    """
    Comprehensive test suite for user management operations.
    
    This class tests all aspects of user CRUD operations including:
    - Data validation and sanitization
    - Password strength requirements
    - Geolocation data handling
    - Error scenarios and edge cases
    - Security considerations (password exposure prevention)
    
    Test Strategy:
    - Positive testing: Valid data scenarios
    - Negative testing: Invalid data and edge cases
    - Security testing: Password exposure prevention
    - Data integrity: Unique constraints and validation
    """
    
    def test_create_user_success(self, test_client: TestClient, db: Session):
        """
        Test successful user creation with complete valid data.
        
        Test Scenario:
            1. Prepare user data with all fields (email, name, password, geolocation)
            2. Submit POST request to /users/ endpoint
            3. Verify successful response (200 status)
            4. Validate all returned data matches input data
            5. Ensure sensitive data (password_hash) is not exposed
            6. Verify default values (is_admin=False)
        
        Expected Result:
            - HTTP 200 (Success)
            - All user data correctly stored and returned
            - Password hash not exposed in response
            - Default admin status set to False
        """
        # Prepare comprehensive user data including geolocation
        user_data = {
            "email": "test@example.com",
            "name": "Test User",
            "password": "Test123!",
            "latitude": 51.5074,      # London coordinates
            "longitude": -0.1278,
            "city": "London",
            "country": "UK"
        }
        
        # Submit user creation request
        response = test_client.post(
            "/users/",
            json=user_data
        )
        
        # Verify successful creation
        assert response.status_code == 200, "User creation should succeed with 200 status"
        
        # Validate response data
        data = response.json()
        assert data["email"] == user_data["email"], "Email should match input"
        assert data["name"] == user_data["name"], "Name should match input"
        assert data["latitude"] == user_data["latitude"], "Latitude should match input"
        assert data["longitude"] == user_data["longitude"], "Longitude should match input"
        assert data["city"] == user_data["city"], "City should match input"
        assert data["country"] == user_data["country"], "Country should match input"
        assert data["is_admin"] == False, "Default admin status should be False"
        assert "id" in data, "Response should contain user ID"
        assert "password_hash" not in data, "Password hash should not be exposed"
    
    def test_create_user_minimal_data(self, test_client: TestClient, db: Session):
        """
        Test user creation with only required fields (minimal data).
        
        Test Scenario:
            1. Prepare user data with only essential fields (email, name, password)
            2. Submit POST request to /users/ endpoint
            3. Verify successful response (200 status)
            4. Validate required fields are stored correctly
            5. Ensure optional fields default to None
        
        Expected Result:
            - HTTP 200 (Success)
            - Required fields stored and returned correctly
            - Optional geolocation fields default to None
        """
        # Prepare minimal user data (only required fields)
        user_data = {
            "email": "minimal@example.com",
            "name": "Minimal User",
            "password": "Minimal123!"
        }
        
        # Submit user creation request
        response = test_client.post(
            "/users/",
            json=user_data
        )
        
        # Verify successful creation
        assert response.status_code == 200, "Minimal user creation should succeed"
        
        # Validate response data
        data = response.json()
        assert data["email"] == user_data["email"], "Email should match input"
        assert data["name"] == user_data["name"], "Name should match input"
        # Verify optional fields default to None
        assert data["latitude"] is None, "Latitude should default to None"
        assert data["longitude"] is None, "Longitude should default to None"
        assert data["city"] is None, "City should default to None"
        assert data["country"] is None, "Country should default to None"
    
    def test_create_user_duplicate_email(self, test_client: TestClient, db: Session):
        """
        Test user creation fails when attempting to create duplicate email.
        
        Test Scenario:
            1. Create first user with unique email
            2. Attempt to create second user with identical email
            3. Verify first creation succeeds (200 status)
            4. Verify second creation fails (400 status)
            5. Validate error response indicates duplicate email
        
        Expected Result:
            - First user: HTTP 200 (Success)
            - Second user: HTTP 400 (Bad Request - Duplicate)
            - Error message indicates email uniqueness violation
        """
        # Create first user successfully
        user_data = {
            "email": "duplicate@example.com",
            "name": "First User",
            "password": "First123!"
        }
        
        response = test_client.post("/users/", json=user_data)
        assert response.status_code == 200, "First user should be created successfully"
        
        # Attempt to create second user with identical email
        duplicate_data = {
            "email": "duplicate@example.com",  # Same email as first user
            "name": "Second User",
            "password": "Second123!"
        }
        
        response = test_client.post("/users/", json=duplicate_data)
        assert response.status_code == 400, "Duplicate email should return 400 status"
    
    def test_password_validation_too_short(self, test_client: TestClient, db: Session):
        """
        Test password validation fails for passwords shorter than 8 characters.
        
        Test Scenario:
            1. Prepare user data with password less than 8 characters
            2. Submit POST request to /users/ endpoint
            3. Verify validation failure (422 status)
            4. Validate error message indicates minimum length requirement
        
        Expected Result:
            - HTTP 422 (Unprocessable Entity)
            - Error message specifies 8-character minimum requirement
        """
        # Prepare user data with short password (7 characters)
        user_data = {
            "email": "short@example.com",
            "name": "Short Password User",
            "password": "Short1"  # Only 7 characters (below minimum)
        }
        
        # Submit user creation request
        response = test_client.post("/users/", json=user_data)
        assert response.status_code == 422, "Short password should trigger validation error"
        
        # Validate error message content
        error_detail = response.json()["detail"][0]
        assert "Password must be at least 8 characters long" in error_detail["msg"], (
            "Error message should specify minimum length requirement"
        )
    
    def test_password_validation_no_uppercase(self, test_client: TestClient, db: Session):
        """
        Test password validation fails for passwords without uppercase letters.
        
        Test Scenario:
            1. Prepare user data with password containing no uppercase letters
            2. Submit POST request to /users/ endpoint
            3. Verify validation failure (422 status)
            4. Validate error message indicates uppercase requirement
        
        Expected Result:
            - HTTP 422 (Unprocessable Entity)
            - Error message specifies uppercase letter requirement
        """
        # Prepare user data with password lacking uppercase letters
        user_data = {
            "email": "noupper@example.com",
            "name": "No Uppercase User",
            "password": "nouppercase123!"  # No uppercase letters
        }
        
        # Submit user creation request
        response = test_client.post("/users/", json=user_data)
        assert response.status_code == 422, "Password without uppercase should trigger validation error"
        
        # Validate error message content
        error_detail = response.json()["detail"][0]
        assert "Password must contain at least one uppercase letter" in error_detail["msg"], (
            "Error message should specify uppercase letter requirement"
        )
    
    def test_password_validation_no_lowercase(self, test_client: TestClient, db: Session):
        """
        Test password validation fails for passwords without lowercase letters.
        
        Test Scenario:
            1. Prepare user data with password containing no lowercase letters
            2. Submit POST request to /users/ endpoint
            3. Verify validation failure (422 status)
            4. Validate error message indicates lowercase requirement
        
        Expected Result:
            - HTTP 422 (Unprocessable Entity)
            - Error message specifies lowercase letter requirement
        """
        # Prepare user data with password lacking lowercase letters
        user_data = {
            "email": "nolower@example.com",
            "name": "No Lowercase User",
            "password": "NOLOWERCASE123!"  # No lowercase letters
        }
        
        # Submit user creation request
        response = test_client.post("/users/", json=user_data)
        assert response.status_code == 422, "Password without lowercase should trigger validation error"
        
        # Validate error message content
        error_detail = response.json()["detail"][0]
        assert "Password must contain at least one lowercase letter" in error_detail["msg"], (
            "Error message should specify lowercase letter requirement"
        )
    
    def test_password_validation_no_digit(self, test_client: TestClient, db: Session):
        """
        Test password validation fails for passwords without numeric digits.
        
        Test Scenario:
            1. Prepare user data with password containing no digits
            2. Submit POST request to /users/ endpoint
            3. Verify validation failure (422 status)
            4. Validate error message indicates digit requirement
        
        Expected Result:
            - HTTP 422 (Unprocessable Entity)
            - Error message specifies digit requirement
        """
        # Prepare user data with password lacking digits
        user_data = {
            "email": "nodigit@example.com",
            "name": "No Digit User",
            "password": "NoDigit!"  # No numeric digits
        }
        
        # Submit user creation request
        response = test_client.post("/users/", json=user_data)
        assert response.status_code == 422, "Password without digits should trigger validation error"
        
        # Validate error message content
        error_detail = response.json()["detail"][0]
        assert "Password must contain at least one digit" in error_detail["msg"], (
            "Error message should specify digit requirement"
        )
    
    def test_password_validation_no_special_char(self, test_client: TestClient, db: Session):
        """
        Test password validation fails for passwords without special characters.
        
        Test Scenario:
            1. Prepare user data with password containing no special characters
            2. Submit POST request to /users/ endpoint
            3. Verify validation failure (422 status)
            4. Validate error message indicates special character requirement
        
        Expected Result:
            - HTTP 422 (Unprocessable Entity)
            - Error message specifies special character requirement
        """
        # Prepare user data with password lacking special characters
        user_data = {
            "email": "nospecial@example.com",
            "name": "No Special Char User",
            "password": "NoSpecial123"  # No special characters
        }
        
        # Submit user creation request
        response = test_client.post("/users/", json=user_data)
        assert response.status_code == 422, "Password without special characters should trigger validation error"
        
        # Validate error message content
        error_detail = response.json()["detail"][0]
        assert "Password must contain at least one special character" in error_detail["msg"], (
            "Error message should specify special character requirement"
        )
    
    def test_password_validation_valid_password(self, test_client: TestClient, db: Session):
        """
        Test password validation passes for various valid password formats.
        
        Test Scenario:
            1. Prepare multiple user data sets with different valid passwords
            2. Submit POST requests for each valid password
            3. Verify all validations pass (200 status)
            4. Test various special character combinations
        
        Expected Result:
            - All valid passwords: HTTP 200 (Success)
            - Various special characters accepted (!, @, #, $)
            - Mixed case, digits, and special characters work
        """
        # Test various valid password formats
        valid_passwords = [
            "Valid123!",      # Basic special character
            "StrongP@ss1",   # @ symbol
            "Complex#Pass2", # # symbol
            "Secure$Pass3"   # $ symbol
        ]
        
        # Test each valid password
        for i, password in enumerate(valid_passwords):
            user_data = {
                "email": f"valid{i}@example.com",
                "name": f"Valid User {i}",
                "password": password
            }
            
            response = test_client.post("/users/", json=user_data)
            assert response.status_code == 200, f"Password '{password}' should be valid"
    
    def test_list_users_success(self, test_client: TestClient, db: Session):
        """
        Test successful listing of all users in the system.
        
        Test Scenario:
            1. Create multiple test users with unique data
            2. Submit GET request to /users/ endpoint
            3. Verify successful response (200 status)
            4. Validate response contains expected number of users
            5. Ensure sensitive data (passwords) are not exposed
        
        Expected Result:
            - HTTP 200 (Success)
            - Response contains at least the created users
            - No password or password_hash fields exposed
            - User data integrity maintained
        """
        # Create test users for listing
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
        
        # Create users in database
        test_client.post("/users/", json=user1_data)
        test_client.post("/users/", json=user2_data)
        
        # Retrieve list of all users
        response = test_client.get("/users/")
        assert response.status_code == 200, "User listing should succeed"
        
        # Validate response data
        users = response.json()
        assert len(users) >= 2, "Response should contain at least the created users"
        
        # Verify sensitive data is not exposed
        for user in users:
            assert "password_hash" not in user, "Password hash should not be exposed"
            assert "password" not in user, "Password should not be exposed"
    
    def test_get_user_by_id_success(self, test_client: TestClient, db: Session):
        """
        Test successful retrieval of specific user by their unique ID.
        
        Test Scenario:
            1. Create a test user and capture their ID
            2. Submit GET request to /users/{id} endpoint
            3. Verify successful response (200 status)
            4. Validate returned data matches created user data
            5. Ensure sensitive data (password_hash) is not exposed
        
        Expected Result:
            - HTTP 200 (Success)
            - User data matches creation data exactly
            - No password or password_hash fields exposed
            - User ID correctly returned
        """
        # Create a test user first
        user_data = {
            "email": "getbyid1@example.com",
            "name": "Get By ID User",
            "password": "Get123!@"
        }
        
        create_response = test_client.post("/users/", json=user_data)
        assert create_response.status_code == 200, "User creation should succeed"
        
        # Extract user ID from creation response
        user_id = create_response.json()["id"]
        
        # Retrieve user by their ID
        response = test_client.get(f"/users/{user_id}")
        assert response.status_code == 200, "User retrieval by ID should succeed"
        
        # Validate response data
        data = response.json()
        assert data["id"] == user_id, "Returned user ID should match requested ID"
        assert data["email"] == user_data["email"], "Email should match creation data"
        assert data["name"] == user_data["name"], "Name should match creation data"
        assert "password_hash" not in data, "Password hash should not be exposed"
    
    def test_get_user_by_id_not_found(self, test_client: TestClient, db: Session):
        """
        Test user retrieval fails for non-existent user ID.
        
        Test Scenario:
            1. Submit GET request to /users/{id} with non-existent ID (999)
            2. Verify proper error response (404 status)
            3. Validate error message indicates user not found
        
        Expected Result:
            - HTTP 404 (Not Found)
            - Error message indicates "User not found"
        """
        # Attempt to retrieve non-existent user
        response = test_client.get("/users/999")
        assert response.status_code == 404, "Non-existent user should return 404"
        assert "User not found" in response.json()["detail"], (
            "Error message should indicate user not found"
        )
    
    def test_update_user_success(self, test_client: TestClient, db: Session):
        """
        Test successful user data update with complete information.
        
        Test Scenario:
            1. Create a test user and capture their ID
            2. Prepare updated user data (email, name, password, geolocation)
            3. Submit PUT request to /users/{id} endpoint
            4. Verify successful response (200 status)
            5. Validate all updated data is correctly stored and returned
        
        Expected Result:
            - HTTP 200 (Success)
            - All updated fields correctly stored
            - Geolocation data properly updated
            - User information reflects changes
        """
        # Create initial user for updating
        user_data = {
            "email": "update@example.com",
            "name": "Original Name",
            "password": "Update123!"
        }
        
        create_response = test_client.post("/users/", json=user_data)
        assert create_response.status_code == 200, "Initial user creation should succeed"
        
        # Extract user ID for update operation
        user_id = create_response.json()["id"]
        
        # Prepare comprehensive update data
        update_data = {
            "email": "updated@example.com",
            "name": "Updated Name",
            "password": "NewPass123!",
            "latitude": 52.2053,      # Cambridge coordinates
            "longitude": 0.1218,
            "city": "Cambridge",
            "country": "UK"
        }
        
        # Submit user update request
        response = test_client.put(f"/users/{user_id}", json=update_data)
        assert response.status_code == 200, "User update should succeed"
        
        # Validate updated data
        data = response.json()
        assert data["email"] == update_data["email"], "Email should be updated"
        assert data["name"] == update_data["name"], "Name should be updated"
        assert data["latitude"] == update_data["latitude"], "Latitude should be updated"
        assert data["longitude"] == update_data["longitude"], "Longitude should be updated"
        assert data["city"] == update_data["city"], "City should be updated"
        assert data["country"] == update_data["country"], "Country should be updated"
    
    def test_update_user_not_found(self, test_client: TestClient, db: Session):
        """
        Test user update fails for non-existent user ID.
        
        Test Scenario:
            1. Submit PUT request to /users/{id} with non-existent ID (999)
            2. Verify proper error response (404 status)
            3. Validate error message indicates user not found
        
        Expected Result:
            - HTTP 404 (Not Found)
            - Error message indicates "User not found"
        """
        # Prepare update data for non-existent user
        update_data = {
            "email": "nonexistent@example.com",
            "name": "Non-existent User",
            "password": "Pass123!"
        }
        
        # Attempt to update non-existent user
        response = test_client.put("/users/999", json=update_data)
        assert response.status_code == 404, "Non-existent user update should return 404"
        assert "User not found" in response.json()["detail"], (
            "Error message should indicate user not found"
        )
    
    def test_update_user_password_validation(self, test_client: TestClient, db: Session):
        """
        Test password validation during user update operations.
        
        Test Scenario:
            1. Create a test user with valid password
            2. Attempt to update user with invalid password
            3. Verify validation failure (422 status)
            4. Ensure original user data remains unchanged
        
        Expected Result:
            - HTTP 422 (Unprocessable Entity)
            - Password validation error triggered
            - User data remains unchanged
        """
        # Create user with valid password
        user_data = {
            "email": "updatepass@example.com",
            "name": "Update Pass User",
            "password": "Valid123!"
        }
        
        create_response = test_client.post("/users/", json=user_data)
        assert create_response.status_code == 200, "User creation should succeed"
        
        # Extract user ID for update operation
        user_id = create_response.json()["id"]
        
        # Attempt to update with invalid password
        invalid_update_data = {
            "email": "updatepass@example.com",
            "name": "Update Pass User",
            "password": "weak"  # Invalid password (too short, no complexity)
        }
        
        # Submit invalid update request
        response = test_client.put(f"/users/{user_id}", json=invalid_update_data)
        assert response.status_code == 422, "Invalid password should trigger validation error"
    
    def test_delete_user_success(self, test_client: TestClient, db: Session):
        """
        Test successful user deletion and cleanup.
        
        Test Scenario:
            1. Create a test user and capture their ID
            2. Submit DELETE request to /users/{id} endpoint
            3. Verify successful deletion (200 status)
            4. Validate success message
            5. Confirm user is no longer retrievable (404 status)
        
        Expected Result:
            - HTTP 200 (Success)
            - Success message indicates "User deleted"
            - Subsequent GET request returns 404 (Not Found)
        """
        # Create user for deletion testing
        user_data = {
            "email": "delete@example.com",
            "name": "Delete User",
            "password": "Delete123!"
        }
        
        create_response = test_client.post("/users/", json=user_data)
        assert create_response.status_code == 200, "User creation should succeed"
        
        # Extract user ID for deletion
        user_id = create_response.json()["id"]
        
        # Submit user deletion request
        response = test_client.delete(f"/users/{user_id}")
        assert response.status_code == 200, "User deletion should succeed"
        assert "User deleted" in response.json()["message"], (
            "Success message should indicate user deletion"
        )
        
        # Verify user is actually deleted
        get_response = test_client.get(f"/users/{user_id}")
        assert get_response.status_code == 404, "Deleted user should not be retrievable"
    
    def test_delete_user_not_found(self, test_client: TestClient, db: Session):
        """
        Test user deletion fails for non-existent user ID.
        
        Test Scenario:
            1. Submit DELETE request to /users/{id} with non-existent ID (999)
            2. Verify proper error response (404 status)
            3. Validate error message indicates user not found
        
        Expected Result:
            - HTTP 404 (Not Found)
            - Error message indicates "User not found"
        """
        # Attempt to delete non-existent user
        response = test_client.delete("/users/999")
        assert response.status_code == 404, "Non-existent user deletion should return 404"
        assert "User not found" in response.json()["detail"], (
            "Error message should indicate user not found"
        )
    
    def test_user_with_geolocation(self, test_client: TestClient, db: Session):
        """
        Test user creation and retrieval with comprehensive geolocation data.
        
        Test Scenario:
            1. Create user with complete geolocation information
            2. Verify all geolocation fields are stored correctly
            3. Retrieve user and validate geolocation data integrity
            4. Test coordinates, city, and country fields
        
        Expected Result:
            - HTTP 200 (Success) for both creation and retrieval
            - All geolocation fields stored and returned correctly
            - Data integrity maintained between creation and retrieval
        """
        # Prepare user data with comprehensive geolocation
        user_data = {
            "email": "geo1@example.com",
            "name": "Geo User",
            "password": "Geo123!@",
            "latitude": 40.7128,      # New York coordinates
            "longitude": -74.0060,
            "city": "New York",
            "country": "USA"
        }
        
        # Create user with geolocation data
        response = test_client.post("/users/", json=user_data)
        assert response.status_code == 200, "User creation with geolocation should succeed"
        
        # Validate creation response data
        data = response.json()
        assert data["latitude"] == 40.7128, "Latitude should match input"
        assert data["longitude"] == -74.0060, "Longitude should match input"
        assert data["city"] == "New York", "City should match input"
        assert data["country"] == "USA", "Country should match input"
        
        # Retrieve user to verify data persistence
        user_id = data["id"]
        get_response = test_client.get(f"/users/{user_id}")
        assert get_response.status_code == 200, "User retrieval should succeed"
        
        # Validate retrieved geolocation data
        retrieved_data = get_response.json()
        assert retrieved_data["latitude"] == 40.7128, "Retrieved latitude should match"
        assert retrieved_data["longitude"] == -74.0060, "Retrieved longitude should match"
        assert retrieved_data["city"] == "New York", "Retrieved city should match"
        assert retrieved_data["country"] == "USA", "Retrieved country should match"
    
    def test_user_email_validation(self, test_client: TestClient, db: Session):
        """
        Test email validation for various valid email formats.
        
        Test Scenario:
            1. Prepare multiple user data sets with different email formats
            2. Test various domain extensions (.com, .co.uk, .org)
            3. Submit POST requests for each valid email format
            4. Verify all validations pass (200 status)
        
        Expected Result:
            - All valid email formats: HTTP 200 (Success)
            - Various domain extensions accepted
            - Email validation working correctly
        """
        # Test various valid email formats
        valid_emails = [
            "email1@example.com",    # Standard .com domain
            "email2@domain.co.uk",   # UK domain
            "email3@example.org",    # .org domain
            "email4@numbers.com"     # Domain with numbers
        ]
        
        # Test each valid email format
        for i, email in enumerate(valid_emails):
            user_data = {
                "email": email,
                "name": f"Email User {i}",
                "password": "Email123!"
            }
            
            response = test_client.post("/users/", json=user_data)
            assert response.status_code == 200, f"Email '{email}' should be valid"
    
    def test_user_name_validation(self, test_client: TestClient, db: Session):
        """
        Test name validation for various valid name formats and characters.
        
        Test Scenario:
            1. Prepare multiple user data sets with different name formats
            2. Test international characters, special characters, numbers
            3. Test edge cases like long names and special formatting
            4. Submit POST requests for each valid name format
            5. Verify all validations pass (200 status)
        
        Expected Result:
            - All valid name formats: HTTP 200 (Success)
            - International characters accepted
            - Special characters and numbers accepted
            - Long names handled correctly
        """
        # Test various valid name formats including edge cases
        valid_names = [
            "John Doe",              # Standard English name
            "José María",            # International characters
            "李小明",                # Chinese characters
            "O'Connor",              # Special characters (apostrophe)
            "123 Numbers",           # Numbers in name
            "A" * 100               # Long name (100 characters)
        ]
        
        # Test each valid name format
        for i, name in enumerate(valid_names):
            user_data = {
                "email": f"name{i}@example.com",
                "name": name,
                "password": "Name123!"
            }         
            response = test_client.post("/users/", json=user_data)
            assert response.status_code == 200, f"Name '{name}' should be valid"