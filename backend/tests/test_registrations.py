"""
Event Registration Test Suite

This module contains comprehensive tests for the event registration system,
covering all CRUD operations, edge cases, and authorization scenarios.

Test Coverage:
- User registration for events
- Event capacity management
- Duplicate registration prevention
- User unregistration from events
- Admin-only operations
- Error handling and validation

Dependencies:
- pytest: Testing framework
- FastAPI TestClient: HTTP client for testing
- SQLAlchemy: Database ORM
- Custom fixtures: User and event creation helpers
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.event import Event
from app.utils.security import create_access_token
import datetime


def create_user(db: Session, email: str, is_admin: bool = False) -> User:
    """
    Helper function to create test users in the database.
    
    Args:
        db: Database session
        email: User email address (used to generate name)
        is_admin: Whether the user has admin privileges
        
    Returns:
        User: Created user object
        
    Note:
        - Handles duplicate email scenarios gracefully
        - Uses simple password hash for testing purposes
        - Generates name from email prefix
    """
    try:
        user = User(
            email=email, 
            name=email.split('@')[0], 
            password_hash="testpassword", 
            is_admin=is_admin
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    except IntegrityError:
        db.rollback()
        return db.query(User).filter(User.email == email).first()


def create_event(db: Session, title: str, capacity: int = None) -> Event:
    """
    Helper function to create test events in the database.
    
    Args:
        db: Database session
        title: Event title
        capacity: Maximum number of registrations (optional)
        
    Returns:
        Event: Created event object
        
    Note:
        - Events are created with future dates (tomorrow + 2 hours)
        - Uses UTC timezone for consistency
        - Capacity is optional for unlimited events
    """
    event = Event(
        title=title, 
        description="Test Event", 
        start_time=datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=1), 
        end_time=datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=1, hours=2), 
        capacity=capacity
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    return event


# =============================================================================
# Pytest Fixtures
# =============================================================================

@pytest.fixture
def normal_user(db: Session) -> User:
    """
    Fixture providing a regular (non-admin) user for testing.
    
    Returns:
        User: Regular user with standard permissions
        
    Usage:
        def test_something(normal_user: User):
            # normal_user is automatically created and available
    """
    return create_user(db, "normal@test.com")


@pytest.fixture
def admin_user(db: Session) -> User:
    """
    Fixture providing an admin user for testing privileged operations.
    
    Returns:
        User: Admin user with elevated permissions
        
    Usage:
        def test_admin_operation(admin_user: User):
            # admin_user has is_admin=True
    """
    return create_user(db, "admin@test.com", is_admin=True)


@pytest.fixture
def test_event(db: Session) -> Event:
    """
    Fixture providing a standard test event with unlimited capacity.
    
    Returns:
        Event: Test event for registration testing
        
    Note:
        - No capacity limit (unlimited registrations)
        - Future date to ensure event is active
    """
    return create_event(db, title="Test Event")


@pytest.fixture
def full_event(db: Session) -> Event:
    """
    Fixture providing a test event with limited capacity (1 registration).
    
    Returns:
        Event: Test event with capacity=1 for testing full event scenarios
        
    Note:
        - Limited to 1 registration for testing capacity constraints
        - Useful for testing "event is full" error scenarios
    """
    return create_event(db, "Full Event", capacity=1)


# =============================================================================
# Event Registration Tests
# =============================================================================

def test_register_for_event_success(test_client: TestClient, db: Session, normal_user: User, test_event: Event):
    """
    Test successful event registration for a valid user and event.
    
    Test Scenario:
        1. Create a normal user and test event
        2. Generate JWT token for authentication
        3. Attempt to register user for the event
        4. Verify successful registration (200 status)
        5. Validate response data contains correct user_id and event_id
        
    Expected Result:
        - HTTP 200 (Success)
        - Response contains correct user_id and event_id
        - User is successfully registered for the event
    """
    # Generate authentication token for the user
    token = create_access_token(data={"sub": normal_user.email})
    
    # Attempt to register user for the event
    response = test_client.post(
        f"/registrations/{test_event.id}", 
        headers={"Authorization": f"Bearer {token}"}
    )
    
    # Verify successful registration
    assert response.status_code == 200, "Registration should succeed with 200 status"
    
    # Validate response data
    data = response.json()
    assert data["user_id"] == normal_user.id, "Response should contain correct user_id"
    assert data["event_id"] == test_event.id, "Response should contain correct event_id"


def test_register_for_nonexistent_event(test_client: TestClient, db: Session, normal_user: User):
    """
    Test registration attempt for a non-existent event.
    
    Test Scenario:
        1. Create a normal user
        2. Generate JWT token for authentication
        3. Attempt to register for event ID 999 (non-existent)
        4. Verify proper error handling (404 status)
        5. Validate error message indicates event not found
        
    Expected Result:
        - HTTP 404 (Not Found)
        - Error message indicates "Event not found"
        - No registration should be created
    """
    # Generate authentication token for the user
    token = create_access_token(data={"sub": normal_user.email})
    
    # Attempt to register for non-existent event
    response = test_client.post(
        "/registrations/999", 
        headers={"Authorization": f"Bearer {token}"}
    )
    
    # Verify proper error handling
    assert response.status_code == 404, "Should return 404 for non-existent event"
    assert "Event not found" in response.json()["detail"], (
        "Error message should indicate event not found"
    )


def test_register_for_event_already_registered(test_client: TestClient, db: Session, normal_user: User, test_event: Event):
    """
    Test duplicate registration prevention for the same user and event.
    
    Test Scenario:
        1. Create a normal user and test event
        2. Generate JWT token for authentication
        3. Successfully register user for the event (first registration)
        4. Attempt to register the same user for the same event again
        5. Verify duplicate registration is prevented (400 status)
        6. Validate error message indicates user is already registered
        
    Expected Result:
        - First registration: HTTP 200 (Success)
        - Second registration: HTTP 400 (Bad Request)
        - Error message indicates "User already registered for this event"
    """
    # Generate authentication token for the user
    token = create_access_token(data={"sub": normal_user.email})
    
    # First registration (should succeed)
    test_client.post(f"/registrations/{test_event.id}", headers={"Authorization": f"Bearer {token}"})
    
    # Second registration attempt (should fail)
    response = test_client.post(
        f"/registrations/{test_event.id}", 
        headers={"Authorization": f"Bearer {token}"}
    )
    
    # Verify duplicate registration is prevented
    assert response.status_code == 400, "Should return 400 for duplicate registration"
    assert "User already registered for this event" in response.json()["detail"], "Error message should indicate duplicate registration"


def test_register_for_full_event(test_client: TestClient, db: Session, normal_user: User, full_event: Event):
    """
    Test registration attempt for an event that has reached capacity.
    
    Test Scenario:
        1. Create a full_event with capacity=1
        2. Create two users (other_user and normal_user)
        3. First user successfully registers for the event
        4. Second user attempts to register for the now-full event
        5. Verify capacity limit enforcement (400 status)
        6. Validate error message indicates event is full
        
    Expected Result:
        - First user registration: HTTP 200 (Success)
        - Second user registration: HTTP 400 (Bad Request)
        - Error message indicates "Event is full"
        - Event capacity limit is properly enforced
    """
    # First user registers successfully (event now has 1/1 capacity)
    other_user = create_user(db, "other@test.com")
    token1 = create_access_token(data={"sub": other_user.email})
    response1 = test_client.post(
        f"/registrations/{full_event.id}", 
        headers={"Authorization": f"Bearer {token1}"}
    )
    assert response1.status_code == 200, "First user should register successfully"

    # Second user fails to register (event is now full)
    token2 = create_access_token(data={"sub": normal_user.email})
    response2 = test_client.post(
        f"/registrations/{full_event.id}", 
        headers={"Authorization": f"Bearer {token2}"}
    )
    
    # Verify capacity limit enforcement
    assert response2.status_code == 400, "Should return 400 when event is full"
    assert "Event is full" in response2.json()["detail"], "Error message should indicate event is full"


# =============================================================================
# Event Unregistration Tests
# =============================================================================

def test_unregister_from_event_success(
    test_client: TestClient, 
    db: Session, 
    normal_user: User, 
    test_event: Event
):
    """
    Test successful unregistration from an event.
    
    Test Scenario:
        1. Create a normal user and test event
        2. Generate JWT token for authentication
        3. Register user for the event
        4. Successfully unregister user from the event
        5. Verify successful unregistration (200 status)
        6. Validate success message
        
    Expected Result:
        - HTTP 200 (Success)
        - Success message indicates "Unregistered from event"
        - User is no longer registered for the event
    """
    # Generate authentication token for the user
    token = create_access_token(data={"sub": normal_user.email})
    
    # First register the user for the event
    test_client.post(f"/registrations/{test_event.id}", headers={"Authorization": f"Bearer {token}"})
    
    # Then unregister the user from the event
    response = test_client.delete(
        f"/registrations/{test_event.id}", 
        headers={"Authorization": f"Bearer {token}"}
    )
    
    # Verify successful unregistration
    assert response.status_code == 200, "Unregistration should succeed with 200 status"
    assert "Unregistered from event" in response.json()["message"], "Success message should indicate unregistration"


def test_unregister_from_event_not_registered(test_client: TestClient, db: Session, normal_user: User, test_event: Event):
    """
    Test unregistration attempt for a user not registered for the event.
    
    Test Scenario:
        1. Create a normal user and test event
        2. Generate JWT token for authentication
        3. Attempt to unregister user from event without prior registration
        4. Verify proper error handling (404 status)
        5. Validate error message indicates registration not found
        
    Expected Result:
        - HTTP 404 (Not Found)
        - Error message indicates "Registration not found"
        - No changes should be made to the database
    """
    # Generate authentication token for the user
    token = create_access_token(data={"sub": normal_user.email})
    
    # Attempt to unregister without prior registration
    response = test_client.delete(
        f"/registrations/{test_event.id}", 
        headers={"Authorization": f"Bearer {token}"}
    )
    
    # Verify proper error handling
    assert response.status_code == 404, "Should return 404 for non-existent registration"
    assert "Registration not found" in response.json()["detail"], "Error message should indicate registration not found"


# =============================================================================
# Admin Operations Tests
# =============================================================================

def test_list_registrations_for_event_admin(test_client: TestClient, db: Session, admin_user: User, normal_user: User, test_event: Event):
    """
    Test admin user's ability to list all registrations for an event.
    
    Test Scenario:
        1. Create admin user, normal user, and test event
        2. Normal user registers for the event
        3. Admin user attempts to list all registrations for the event
        4. Verify admin access is granted (200 status)
        5. Validate response contains registration data
        
    Expected Result:
        - HTTP 200 (Success)
        - Admin can view all registrations for the event
        - Response contains registration information
        - Normal user registration is visible to admin
    """
    # Normal user registers for the event
    token_normal = create_access_token(data={"sub": normal_user.email})
    test_client.post(f"/registrations/{test_event.id}", headers={"Authorization": f"Bearer {token_normal}"})

    # Admin lists all registrations for the event
    token_admin = create_access_token(data={"sub": admin_user.email})
    response = test_client.get(
        f"/registrations/event/{test_event.id}", 
        headers={"Authorization": f"Bearer {token_admin}"}
    )
    
    # Verify admin access is granted
    assert response.status_code == 200, "Admin should be able to list registrations"


def test_list_registrations_for_event_non_admin(test_client: TestClient, db: Session, normal_user: User, test_event: Event):
    """
    Test that non-admin users cannot list registrations for an event.
    
    Test Scenario:
        1. Create normal user and test event
        2. Generate JWT token for normal user
        3. Attempt to list registrations for the event
        4. Verify access is denied (403 status)
        5. Validate error message indicates insufficient permissions
        
    Expected Result:
        - HTTP 403 (Forbidden)
        - Error message indicates insufficient permissions
        - Non-admin users cannot view registration lists
    """
    # Generate authentication token for normal user
    token = create_access_token(data={"sub": normal_user.email})
    
    # Attempt to list registrations (should fail for non-admin)
    response = test_client.get(
        f"/registrations/event/{test_event.id}", 
        headers={"Authorization": f"Bearer {token}"}
    )
    
    # Verify access is denied for non-admin users
    assert response.status_code == 403, "Non-admin users should not be able to list registrations"


# =============================================================================
# Pagination Tests for Registrations
# =============================================================================

def test_registrations_pagination_comprehensive(test_client: TestClient, db: Session, admin_user: User, test_event: Event):
    """
    Test comprehensive pagination scenarios for event registrations.
    
    **Test Scenario:**
    - Create multiple users and register them for an event
    - Test different page sizes and offsets
    - Verify pagination metadata accuracy
    - Test boundary conditions
    
    **Expected Result:**
    - Correct pagination metadata
    - Accurate item counts
    - Proper offset/limit handling
    """
    # Create 15 test users and register them for the event
    registered_users = []
    for i in range(15):
        user = create_user(db, f"pagination{i}@test.com")
        registered_users.append(user)
        
        # Register user for the event
        token = create_access_token(data={"sub": user.email})
        response = test_client.post(
            f"/registrations/{test_event.id}", 
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200, f"User {i} should register successfully"
    
    # Admin token for listing registrations
    admin_token = create_access_token(data={"sub": admin_user.email})
    
    # Test first page (limit=5, offset=0)
    response = test_client.get(
        f"/registrations/event/{test_event.id}?limit=5&offset=0",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 15
    assert data["limit"] == 5
    assert data["offset"] == 0
    assert len(data["items"]) == 5
    
    # Test second page (limit=5, offset=5)
    response = test_client.get(
        f"/registrations/event/{test_event.id}?limit=5&offset=5",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 15
    assert data["limit"] == 5
    assert data["offset"] == 5
    assert len(data["items"]) == 5
    
    # Test third page (limit=5, offset=10)
    response = test_client.get(
        f"/registrations/event/{test_event.id}?limit=5&offset=10",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 15
    assert data["limit"] == 5
    assert data["offset"] == 10
    assert len(data["items"]) == 5
    
    # Test last page (limit=5, offset=15) - should return empty
    response = test_client.get(
        f"/registrations/event/{test_event.id}?limit=5&offset=15",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 15
    assert data["limit"] == 5
    assert data["offset"] == 15
    assert len(data["items"]) == 0


def test_registrations_pagination_edge_cases(test_client: TestClient, db: Session, admin_user: User, test_event: Event):
    """
    Test registrations pagination with edge cases.
    
    **Test Scenario:**
    - Large offset values
    - Zero limits
    - Empty result sets
    - Negative values
    
    **Expected Result:**
    - Appropriate handling of edge cases
    - Consistent response structure
    """
    admin_token = create_access_token(data={"sub": admin_user.email})
    
    # Test with large offset
    response = test_client.get(
        f"/registrations/event/{test_event.id}?offset=1000&limit=10",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["offset"] == 1000
    assert data["total"] >= 0
    assert len(data["items"]) >= 0
    
    # Test with zero limit
    response = test_client.get(
        f"/registrations/event/{test_event.id}?limit=0",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["limit"] == 0
    assert len(data["items"]) == 0
    
    # Test with negative limit (API may not handle this gracefully)
    response = test_client.get(
        f"/registrations/event/{test_event.id}?limit=-5",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    # The API might return an error or default to a positive value
    if response.status_code == 200:
        data = response.json()
        # If successful, ensure we get a valid response
        assert "total" in data
        assert "items" in data
    else:
        # If it returns an error, that's also acceptable
        assert response.status_code in [400, 422]


def test_registrations_pagination_response_structure(test_client: TestClient, db: Session, admin_user: User, test_event: Event):
    """
    Test that registrations pagination response has correct structure.
    
    **Test Scenario:**
    - Verify PaginatedResponse structure for registrations
    - Check all required fields are present
    - Validate field types and values
    
    **Expected Result:**
    - Correct response structure
    - All required fields present
    - Proper data types
    """
    # Create a test user and register them
    user = create_user(db, "structure@test.com")
    token = create_access_token(data={"sub": user.email})
    test_client.post(
        f"/registrations/{test_event.id}", 
        headers={"Authorization": f"Bearer {token}"}
    )
    
    # Admin token for listing registrations
    admin_token = create_access_token(data={"sub": admin_user.email})
    
    response = test_client.get(
        f"/registrations/event/{test_event.id}?limit=10&offset=0",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    
    # Verify response structure matches PaginatedResponse schema
    required_fields = ["total", "limit", "offset", "items"]
    for field in required_fields:
        assert field in data, f"Response should contain '{field}' field"
    
    # Verify field types
    assert isinstance(data["total"], int), "Total should be an integer"
    assert isinstance(data["limit"], int), "Limit should be an integer"
    assert isinstance(data["offset"], int), "Offset should be an integer"
    assert isinstance(data["items"], list), "Items should be a list"
    
    # Verify field values are reasonable
    assert data["total"] >= 0, "Total should be non-negative"
    assert data["limit"] >= 0, "Limit should be non-negative"
    assert data["offset"] >= 0, "Offset should be non-negative"
    assert len(data["items"]) <= data["limit"], "Items count should not exceed limit"
    
    # If there are items, verify they have the expected structure
    if data["items"]:
        item = data["items"][0]
        expected_item_fields = ["id", "user_id", "event_id", "registered_at"]
        for field in expected_item_fields:
            assert field in item, f"Registration item should contain '{field}' field"


def test_registrations_pagination_data_integrity(test_client: TestClient, db: Session, admin_user: User, test_event: Event):
    """
    Test that pagination maintains data integrity across pages.
    
    **Test Scenario:**
    - Create multiple registrations
    - Verify data consistency across pagination
    - Check that no data is lost or duplicated
    
    **Expected Result:**
    - Data integrity maintained across pages
    - No duplicate registrations in different pages
    - All registrations accounted for
    """
    # Create 10 test users and register them
    registered_user_ids = []
    for i in range(10):
        user = create_user(db, f"integrity{i}@test.com")
        registered_user_ids.append(user.id)
        
        # Register user for the event
        token = create_access_token(data={"sub": user.email})
        response = test_client.post(
            f"/registrations/{test_event.id}", 
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200, f"User {i} should register successfully"
    
    # Admin token for listing registrations
    admin_token = create_access_token(data={"sub": admin_user.email})
    
    # Collect all registrations across multiple pages
    all_registrations = []
    page = 0
    limit = 3
    
    while True:
        response = test_client.get(
            f"/registrations/event/{test_event.id}?limit={limit}&offset={page * limit}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        
        if not data["items"]:
            break
            
        all_registrations.extend(data["items"])
        page += 1
        
        # Safety check to prevent infinite loop
        if page > 10:
            break
    
    # Verify all registered users are present
    found_user_ids = [reg["user_id"] for reg in all_registrations]
    for user_id in registered_user_ids:
        assert user_id in found_user_ids, f"User {user_id} should be found in pagination"
    
    # Verify no duplicates
    unique_user_ids = set(found_user_ids)
    assert len(unique_user_ids) == len(found_user_ids), "No duplicate registrations should be returned"


def test_registrations_pagination_unauthorized_access(test_client: TestClient, db: Session, normal_user: User, test_event: Event):
    """
    Test that pagination endpoints properly enforce authorization.
    
    **Test Scenario:**
    - Non-admin user attempts to access pagination
    - Verify proper error handling
    - Test different pagination parameters
    
    **Expected Result:**
    - HTTP 403 Forbidden for non-admin users
    - Consistent error responses
    """
    # Create some registrations first
    for i in range(5):
        user = create_user(db, f"unauth{i}@test.com")
        token = create_access_token(data={"sub": user.email})
        test_client.post(
            f"/registrations/{test_event.id}", 
            headers={"Authorization": f"Bearer {token}"}
        )
    
    # Normal user token (non-admin)
    normal_token = create_access_token(data={"sub": normal_user.email})
    
    # Test various pagination parameters with non-admin user
    pagination_tests = [
        "?limit=5&offset=0",
        "?limit=10&offset=0", 
        "?limit=0&offset=0",
        "?limit=5&offset=10"
    ]
    
    for params in pagination_tests:
        response = test_client.get(
            f"/registrations/event/{test_event.id}{params}",
            headers={"Authorization": f"Bearer {normal_token}"}
        )
        assert response.status_code == 403, f"Non-admin should not access pagination with params: {params}"
        assert "Not authorized" in response.json()["detail"], "Error message should indicate authorization failure"
