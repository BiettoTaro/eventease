from datetime import datetime, timedelta, timezone
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.models import Event
from app.models.user import User
from app.utils.security import get_password_hash, create_access_token
from app.schemas.event import EventCreate
from app.schemas.user import UserCreate


class TestEvents:
    """Test suite for events CRUD, listing, distance validation, filtering, and capacity validation"""
    
    def test_create_event_success(self, test_client: TestClient, db: Session):
        """Test successful event creation by admin user"""
        # Create admin user
        admin_user = User(
            email="admin@test.com",
            name="Admin User",
            password_hash=get_password_hash("Admin123!"),
            is_admin=True
        )
        db.add(admin_user)
        db.commit()
        
        # Create access token
        token = create_access_token({"sub": admin_user.email})
        
        # Event data
        event_data = {
            "title": "Test Event",
            "description": "A test event",
            "address": "123 Test St",
            "city": "Test City",
            "country": "Test Country",
            "capacity": 100,
            "latitude": 51.5074,
            "longitude": -0.1278,
            "start_time": "2025-01-15T10:00:00Z",
            "end_time": "2025-01-15T18:00:00Z"
        }
        
        response = test_client.post(
            "/events/",
            json=event_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == event_data["title"]
        assert data["description"] == event_data["description"]
        assert data["capacity"] == event_data["capacity"]
        assert "id" in data
    
    def test_create_event_unauthorized(self, test_client: TestClient, db: Session):
        """Test event creation fails for non-admin users"""
        # Create regular user
        regular_user = User(
            email="user@test.com",
            name="Regular User",
            password_hash=get_password_hash("User123!"),
            is_admin=False
        )
        db.add(regular_user)
        db.commit()
        
        # Create access token
        token = create_access_token({"sub": regular_user.email})
        
        event_data = {
            "title": "Test Event",
            "description": "A test event",
            "start_time": "2025-01-15T10:00:00Z",
            "end_time": "2025-01-15T18:00:00Z"
        }
        
        response = test_client.post(
            "/events/",
            json=event_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 403
        assert "Not authorized" in response.json()["detail"]
    
    def test_list_events_with_location(self, test_client: TestClient, db: Session):
        """Test event listing with user location for distance-based filtering"""
        # Create user with location
        user = User(
            email="user1@test.com",
            name="Test User",
            password_hash=get_password_hash("User123!"),
            latitude=51.5074,
            longitude=-0.1278,
            city="London",
            country="UK"
        )
        db.add(user)
        db.commit()
        
        # Create events at different distances
        event1 = Event(
            title="Near Event",
            description="Event within 50km",
            latitude=51.5074,
            longitude=-0.1278,
            city="London",
            country="UK",
            start_time=datetime.now(timezone.utc) + timedelta(days=1),
            end_time=datetime.now(timezone.utc) + timedelta(days=1, hours=8)
        )
        
        event2 = Event(
            title="Far Event",
            description="Event outside 50km",
            latitude=52.2053,
            longitude=0.1218,
            city="Cambridge",
            country="UK",
            start_time=datetime.now(timezone.utc) + timedelta(days=2),
            end_time=datetime.now(timezone.utc) + timedelta(days=2, hours=8)
        )
        
        db.add_all([event1, event2])
        db.commit()
        
        # Create access token
        token = create_access_token({"sub": str(user.id)})
        
        response = test_client.get(
            "/events/?radius=50",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        events = response.json()
        assert len(events) >= 1
        # Should return nearby events first
        assert any(e["title"] == "Near Event" for e in events)
    
    def test_list_events_fallback_to_city(self, test_client: TestClient, db: Session):
        """Test event listing falls back to city-based filtering when no coordinates"""
        # Create user with city but no coordinates
        user = User(
            email="user2@test.com",
            name="Test User",
            password_hash=get_password_hash("User123!"),
            city="London",
            country="UK"
        )
        db.add(user)
        db.commit()
        
        # Create events in different cities
        event1 = Event(
            title="London Event",
            description="Event in London",
            city="London",
            country="UK",
            start_time=datetime.now(timezone.utc) + timedelta(days=1),
            end_time=datetime.now(timezone.utc) + timedelta(days=1, hours=8)
        )
        
        event2 = Event(
            title="Manchester Event",
            description="Event in Manchester",
            city="Manchester",
            country="UK",
            start_time=datetime.now(timezone.utc) + timedelta(days=2),
            end_time=datetime.now(timezone.utc) + timedelta(days=2, hours=8)
        )
        
        db.add_all([event1, event2])
        db.commit()
        
        # Create access token
        token = create_access_token({"sub": str(user.id)})
        
        response = test_client.get(
            "/events/",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        events = response.json()
        assert len(events) >= 1
        # Should return London events
        assert any(e["city"] == "London" for e in events)
    
    def test_list_events_fallback_to_country(self, test_client: TestClient, db: Session):
        """Test event listing falls back to country-based filtering when no city"""
        # Create user with country but no city or coordinates
        user = User(
            email="user3@test.com",
            name="Test User",
            password_hash=get_password_hash("User123!"),
            country="UK"
        )
        db.add(user)
        db.commit()
        
        # Create events in different countries
        event1 = Event(
            title="UK Event",
            description="Event in UK",
            country="UK",
            start_time=datetime.now(timezone.utc) + timedelta(days=1),
            end_time=datetime.now(timezone.utc) + timedelta(days=1, hours=8)
        )
        
        event2 = Event(
            title="US Event",
            description="Event in US",
            country="US",
            start_time=datetime.now(timezone.utc) + timedelta(days=2),
            end_time=datetime.now(timezone.utc) + timedelta(days=2, hours=8)
        )
        
        db.add_all([event1, event2])
        db.commit()
        
        # Create access token
        token = create_access_token({"sub": str(user.id)})
        
        response = test_client.get(
            "/events/",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        events = response.json()
        assert len(events) >= 1
        # Should return UK events
        assert any(e["country"] == "UK" for e in events)
    
    def test_list_events_fallback_to_latest(self, test_client: TestClient, db: Session):
        """Test event listing falls back to latest events when no location info"""
        # Create user with no location information
        user = User(
            email="user4@test.com",
            name="Test User",
            password_hash=get_password_hash("User123!")
        )
        db.add(user)
        db.commit()
        
        # Create events with different start times
        event1 = Event(
            title="Old Event",
            description="Old event",
            start_time=datetime.now(timezone.utc) - timedelta(days=10),
            end_time=datetime.now(timezone.utc) - timedelta(days=10, hours=-8)
        )
        
        event2 = Event(
            title="New Event",
            description="New event",
            start_time=datetime.now(timezone.utc) + timedelta(days=10),
            end_time=datetime.now(timezone.utc) + timedelta(days=10, hours=8)
        )
        
        db.add_all([event1, event2])
        db.commit()
        
        # Create access token
        token = create_access_token({"sub": str(user.id)})
        
        response = test_client.get(
            "/events/",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        events = response.json()
        assert len(events) >= 2
        # Should return events ordered by start_time desc (newest first)
        assert events[0]["title"] == "New Event"
    
    def test_update_event_success(self, test_client: TestClient, db: Session):
        """Test successful event update by admin user"""
        # Create admin user
        admin_user = User(
            email="admin1@test.com",
            name="Admin User",
            password_hash=get_password_hash("Admin123!"),
            is_admin=True
        )
        db.add(admin_user)
        db.commit()
        
        # Create event
        event = Event(
            title="Original Title",
            description="Original description",
            start_time=datetime.now(timezone.utc) + timedelta(days=1),
            end_time=datetime.now(timezone.utc) + timedelta(days=1, hours=8)
        )
        db.add(event)
        db.commit()
        
        # Create access token
        token = create_access_token({"sub": admin_user.email})
        
        # Update data
        update_data = {
            "title": "Updated Title",
            "description": "Updated description",
            "start_time": "2025-02-15T10:00:00Z",
            "end_time": "2025-02-15T18:00:00Z"
        }
        
        response = test_client.put(
            f"/events/{event.id}",
            json=update_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated Title"
        assert data["description"] == "Updated description"
    
    def test_update_event_not_found(self, test_client: TestClient, db: Session):
        """Test event update fails for non-existent event"""
        # Create admin user
        admin_user = User(
            email="admin2@test.com",
            name="Admin User",
            password_hash=get_password_hash("Admin123!"),
            is_admin=True
        )
        db.add(admin_user)
        db.commit()
        
        # Create access token
        token = create_access_token({"sub": admin_user.email})
        
        update_data = {
            "title": "Updated Title",
            "description": "Updated description",
            "start_time": "2025-02-15T10:00:00Z",
            "end_time": "2025-02-15T18:00:00Z"
        }
        
        response = test_client.put(
            "/events/999",
            json=update_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 404
        assert "Event not found" in response.json()["detail"]
    
    def test_update_event_unauthorized(self, test_client: TestClient, db: Session):
        """Test event update fails for non-admin users"""
        # Create regular user
        regular_user = User(
            email="user5@test.com",
            name="Regular User",
            password_hash=get_password_hash("User123!"),
            is_admin=False
        )
        db.add(regular_user)
        db.commit()
        
        # Create event
        event = Event(
            title="Test Event",
            description="Test description",
            start_time=datetime.now(timezone.utc) + timedelta(days=1),
            end_time=datetime.now(timezone.utc) + timedelta(days=1, hours=8)
        )
        db.add(event)
        db.commit()
        
        # Create access token
        token = create_access_token({"sub": regular_user.email})
        
        update_data = {
            "title": "Updated Title",
            "description": "Updated description",
            "start_time": "2025-02-15T10:00:00Z",
            "end_time": "2025-02-15T18:00:00Z"
        }
        
        response = test_client.put(
            f"/events/{event.id}",
            json=update_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 403
        assert "Not authorized" in response.json()["detail"]
    
    def test_delete_event_success(self, test_client: TestClient, db: Session):
        """Test successful event deletion by admin user"""
        # Create admin user
        admin_user = User(
            email="admin3@test.com",
            name="Admin User",
            password_hash=get_password_hash("Admin123!"),
            is_admin=True
        )
        db.add(admin_user)
        db.commit()
        
        # Create event
        event = Event(
            title="Test Event",
            description="Test description",
            start_time=datetime.now(timezone.utc) + timedelta(days=1),
            end_time=datetime.now(timezone.utc) + timedelta(days=1, hours=8)
        )
        db.add(event)
        db.commit()
        
        # Create access token
        token = create_access_token({"sub": admin_user.email})
        
        response = test_client.delete(
            f"/events/{event.id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        assert "Event deleted" in response.json()["message"]
        
        # Verify event is deleted
        deleted_event = db.query(Event).filter(Event.id == event.id).first()
        assert deleted_event is None
    
    def test_delete_event_not_found(self, test_client: TestClient, db: Session):
        """Test event deletion fails for non-existent event"""
        # Create admin user
        admin_user = User(
            email="admin4@test.com",
            name="Admin User",
            password_hash=get_password_hash("Admin123!"),
            is_admin=True
        )
        db.add(admin_user)
        db.commit()
        
        # Create access token
        token = create_access_token({"sub": admin_user.email})
        
        response = test_client.delete(
            "/events/999",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 404
        assert "Event not found" in response.json()["detail"]
    
    def test_delete_event_unauthorized(self, test_client: TestClient, db: Session):
        """Test event deletion fails for non-admin users"""
        # Create regular user
        regular_user = User(
            email="user8@test.com",
            name="Regular User",
            password_hash=get_password_hash("User123!"),
            is_admin=False
        )
        db.add(regular_user)
        db.commit()
        
        # Create event
        event = Event(
            title="Test Event",
            description="Test description",
            start_time=datetime.now(timezone.utc) + timedelta(days=1),
            end_time=datetime.now(timezone.utc) + timedelta(days=1, hours=8)
        )
        db.add(event)
        db.commit()
        
        # Create access token
        token = create_access_token({"sub": regular_user.email})
        
        response = test_client.delete(
            f"/events/{event.id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 403
        assert "Not authorized" in response.json()["detail"]
    
    def test_distance_validation_haversine(self, test_client: TestClient, db: Session):
        """Test distance calculation using Haversine formula"""
        # Create user with specific coordinates
        user = User(
            email="user6@test.com",
            name="Test User",
            password_hash=get_password_hash("User123!"),
            latitude=51.5074,  # London
            longitude=-0.1278
        )
        db.add(user)
        db.commit()
        
        # Create events at known distances
        # Event 1: Same location (0km)
        event1 = Event(
            title="Same Location",
            description="Event at same coordinates",
            latitude=51.5074,
            longitude=-0.1278,
            start_time=datetime.now(timezone.utc) + timedelta(days=1),
            end_time=datetime.now(timezone.utc) + timedelta(days=1, hours=8)
        )
        
        # Event 2: Cambridge (~80km from London)
        event2 = Event(
            title="Cambridge Event",
            description="Event in Cambridge",
            latitude=52.2053,
            longitude=0.1218,
            start_time=datetime.now(timezone.utc) + timedelta(days=2),
            end_time=datetime.now(timezone.utc) + timedelta(days=2, hours=8)
        )
        
        db.add_all([event1, event2])
        db.commit()
        
        # Create access token
        token = create_access_token({"sub": str(user.id)})
        
        # Test with radius 50km (should only return London event)
        response = test_client.get(
            "/events/?radius=50",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        events = response.json()
        # Should only return events within 50km
        assert all(e["title"] != "Cambridge Event" for e in events)
        
        # Test with radius 100km (should return both events)
        response = test_client.get(
            "/events/?radius=100",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        events = response.json()
        # Should return both events
        assert len(events) >= 2
    
    def test_capacity_validation(self, test_client: TestClient, db: Session):
        """Test event capacity field validation"""
        # Create admin user
        admin_user = User(
            email="admin5@test.com",
            name="Admin User",
            password_hash=get_password_hash("Admin123!"),
            is_admin=True
        )
        db.add(admin_user)
        db.commit()
        
        # Create access token
        token = create_access_token({"sub": admin_user.email})
        
        # Test event with capacity
        event_with_capacity = {
            "title": "Limited Capacity Event",
            "description": "Event with capacity limit",
            "capacity": 50,
            "start_time": "2025-01-15T10:00:00Z",
            "end_time": "2025-01-15T18:00:00Z"
        }
        
        response = test_client.post(
            "/events/",
            json=event_with_capacity,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["capacity"] == 50
        
        # Test event without capacity (should be allowed)
        event_without_capacity = {
            "title": "Unlimited Capacity Event",
            "description": "Event without capacity limit",
            "start_time": "2025-01-15T10:00:00Z",
            "end_time": "2025-01-15T18:00:00Z"
        }
        
        response = test_client.post(
            "/events/",
            json=event_without_capacity,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["capacity"] is None
    
    def test_event_filtering_by_location_priority(self, test_client: TestClient, db: Session):
        """Test event filtering priority: coordinates > city > country > latest"""
        # Create user with all location info
        user = User(
            email="user7@test.com",
            name="Test User",
            password_hash=get_password_hash("User123!"),
            latitude=51.5074,
            longitude=-0.1278,
            city="London",
            country="UK"
        )
        db.add(user)
        db.commit()
        
        # Create events in different locations
        # Event 1: Same coordinates (highest priority)
        event1 = Event(
            title="Exact Location Event",
            description="Event at exact coordinates",
            latitude=51.5074,
            longitude=-0.1278,
            city="London",
            country="UK",
            start_time=datetime.now(timezone.utc) + timedelta(days=1),
            end_time=datetime.now(timezone.utc) + timedelta(days=1, hours=8)
        )
        
        # Event 2: Same city, different coordinates
        event2 = Event(
            title="Same City Event",
            description="Event in same city",
            latitude=51.5075,
            longitude=-0.1279,
            city="London",
            country="UK",
            start_time=datetime.now(timezone.utc) + timedelta(days=2),
            end_time=datetime.now(timezone.utc) + timedelta(days=2, hours=8)
        )
        
        # Event 3: Same country, different city
        event3 = Event(
            title="Same Country Event",
            description="Event in same country",
            city="Manchester",
            country="UK",
            start_time=datetime.now(timezone.utc) + timedelta(days=3),
            end_time=datetime.now(timezone.utc) + timedelta(days=3, hours=8)
        )
        
        # Event 4: Different country
        event4 = Event(
            title="Different Country Event",
            description="Event in different country",
            city="Paris",
            country="France",
            start_time=datetime.now(timezone.utc) + timedelta(days=4),
            end_time=datetime.now(timezone.utc) + timedelta(days=4, hours=8)
        )
        
        db.add_all([event1, event2, event3, event4])
        db.commit()
        
        # Create access token
        token = create_access_token({"sub": str(user.id)})
        
        response = test_client.get(
            "/events/?radius=50",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        events = response.json()
        # Should prioritize events by location (coordinates first)
        assert len(events) >= 1
        # The exact location event should be prioritized
        assert any(e["title"] == "Exact Location Event" for e in events)
    
    def test_events_pagination_comprehensive(self, test_client: TestClient, db: Session):
        """
        Test comprehensive pagination scenarios for events.
        
        **Test Scenario:**
        - Create multiple events
        - Test different page sizes and offsets
        - Verify pagination metadata accuracy
        - Test boundary conditions
        
        **Expected Result:**
        - Correct pagination metadata
        - Accurate item counts
        - Proper offset/limit handling
        """
        # Create user for authentication
        user = User(
            email="pagination@test.com",
            name="Pagination User",
            password_hash=get_password_hash("Pagination123!"),
            is_admin=False
        )
        db.add(user)
        db.commit()
        
        # Create 12 test events
        events = []
        for i in range(12):
            event = Event(
                title=f"Event {i+1}",
                description=f"Description for event {i+1}",
                start_time=datetime.now(timezone.utc) + timedelta(days=i+1),
                end_time=datetime.now(timezone.utc) + timedelta(days=i+1, hours=8)
            )
            events.append(event)
        
        db.add_all(events)
        db.commit()
        
        token = create_access_token({"sub": str(user.id)})
        
        # Test first page (limit=4, offset=0)
        response = test_client.get(
            "/events/?limit=4&offset=0",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 12
        assert data["limit"] == 4
        assert data["offset"] == 0
        assert len(data["items"]) == 4
        
        # Test second page (limit=4, offset=4)
        response = test_client.get(
            "/events/?limit=4&offset=4",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 12
        assert data["limit"] == 4
        assert data["offset"] == 4
        assert len(data["items"]) == 4
        
        # Test third page (limit=4, offset=8)
        response = test_client.get(
            "/events/?limit=4&offset=8",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 12
        assert data["limit"] == 4
        assert data["offset"] == 8
        assert len(data["items"]) == 4
        
        # Test last page (limit=4, offset=12) - should return empty
        response = test_client.get(
            "/events/?limit=4&offset=12",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 12
        assert data["limit"] == 4
        assert data["offset"] == 12
        assert len(data["items"]) == 0
    
    def test_events_pagination_with_radius(self, test_client: TestClient, db: Session):
        """
        Test pagination works correctly with radius filtering.
        
        **Test Scenario:**
        - Create events at different distances
        - Apply radius filter and test pagination
        - Verify radius + pagination combination
        
        **Expected Result:**
        - Pagination works with radius filter
        - Total count reflects filtered results
        - Items respect both radius and pagination
        """
        # Create user with specific location
        user = User(
            email="radius@test.com",
            name="Radius User",
            password_hash=get_password_hash("Radius123!"),
            latitude=51.5074,  # London
            longitude=-0.1278
        )
        db.add(user)
        db.commit()
        
        # Create events at different distances from London
        # Event 1: Same location (0km)
        event1 = Event(
            title="London Event 1",
            description="Event in London",
            latitude=51.5074,
            longitude=-0.1278,
            start_time=datetime.now(timezone.utc) + timedelta(days=1),
            end_time=datetime.now(timezone.utc) + timedelta(days=1, hours=8)
        )
        
        # Event 2: Near London (~10km)
        event2 = Event(
            title="Near London Event 1",
            description="Event near London",
            latitude=51.5075,
            longitude=-0.1279,
            start_time=datetime.now(timezone.utc) + timedelta(days=2),
            end_time=datetime.now(timezone.utc) + timedelta(days=2, hours=8)
        )
        
        # Event 3: Near London (~10km)
        event3 = Event(
            title="Near London Event 2",
            description="Event near London",
            latitude=51.5076,
            longitude=-0.1280,
            start_time=datetime.now(timezone.utc) + timedelta(days=3),
            end_time=datetime.now(timezone.utc) + timedelta(days=3, hours=8)
        )
        
        # Event 4: Far from London (~100km)
        event4 = Event(
            title="Far Event",
            description="Event far from London",
            latitude=52.2053,  # Cambridge
            longitude=0.1218,
            start_time=datetime.now(timezone.utc) + timedelta(days=4),
            end_time=datetime.now(timezone.utc) + timedelta(days=4, hours=8)
        )
        
        db.add_all([event1, event2, event3, event4])
        db.commit()
        
        token = create_access_token({"sub": str(user.id)})
        
        # Test pagination with radius filter (should include nearby events)
        response = test_client.get(
            "/events/?radius=50&limit=2&offset=0",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 3  # Should have at least 3 nearby events
        assert data["limit"] == 2
        assert data["offset"] == 0
        assert len(data["items"]) == 2
        
        # Test second page with radius filter
        response = test_client.get(
            "/events/?radius=50&limit=2&offset=2",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 3
        assert data["limit"] == 2
        assert data["offset"] == 2
        assert len(data["items"]) >= 1  # Should have at least 1 more event
    
    def test_events_pagination_response_structure(self, test_client: TestClient, db: Session):
        """
        Test that events pagination response has correct structure.
        
        **Test Scenario:**
        - Verify PaginatedResponse structure for events
        - Check all required fields are present
        - Validate field types and values
        
        **Expected Result:**
        - Correct response structure
        - All required fields present
        - Proper data types
        """
        # Create user for authentication
        user = User(
            email="structure@test.com",
            name="Structure User",
            password_hash=get_password_hash("Structure123!"),
            is_admin=False
        )
        db.add(user)
        db.commit()
        
        # Create a test event
        event = Event(
            title="Structure Test Event",
            description="Testing response structure",
            start_time=datetime.now(timezone.utc) + timedelta(days=1),
            end_time=datetime.now(timezone.utc) + timedelta(days=1, hours=8)
        )
        db.add(event)
        db.commit()
        
        token = create_access_token({"sub": str(user.id)})
        
        response = test_client.get(
            "/events/?limit=10&offset=0",
            headers={"Authorization": f"Bearer {token}"}
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
            expected_item_fields = ["id", "title", "description", "start_time", "end_time"]
            for field in expected_item_fields:
                assert field in item, f"Event item should contain '{field}' field"