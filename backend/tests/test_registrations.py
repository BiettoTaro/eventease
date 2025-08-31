import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.event import Event
from app.utils.security import create_access_token
import datetime



def create_user(db: Session, email: str, is_admin: bool = False) -> User:
    try:
        user = User(email=email, name=email.split('@')[0], password_hash="testpassword", is_admin=is_admin)
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    except IntegrityError:
        db.rollback()
        return db.query(User).filter(User.email == email).first()

def create_event(db: Session, title: str, capacity: int = None) -> Event:
    event = Event(title=title, description="Test Event", start_time=datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=1), end_time=datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=1, hours=2), capacity=capacity)
    db.add(event)
    db.commit()
    db.refresh(event)
    return event

@pytest.fixture
def normal_user(db: Session) -> User:
    return create_user(db, "normal@test.com")

@pytest.fixture
def admin_user(db: Session) -> User:
    return create_user(db, "admin@test.com", is_admin=True)

@pytest.fixture
def test_event(db: Session) -> Event:
    return create_event(db, title="Test Event")

@pytest.fixture
def full_event(db: Session) -> Event:
    return create_event(db, "Full Event", capacity=1)

def test_register_for_event_success(test_client: TestClient, db: Session, normal_user: User, test_event: Event):
    token = create_access_token(data={"sub": normal_user.email})
    response = test_client.post(f"/registrations/{test_event.id}", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == normal_user.id
    assert data["event_id"] == test_event.id

def test_register_for_nonexistent_event(test_client: TestClient, db: Session, normal_user: User):
    token = create_access_token(data={"sub": normal_user.email})
    response = test_client.post("/registrations/999", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 404
    assert "Event not found" in response.json()["detail"]

def test_register_for_event_already_registered(test_client: TestClient, db: Session, normal_user: User, test_event: Event):
    token = create_access_token(data={"sub": normal_user.email})
    test_client.post(f"/registrations/{test_event.id}", headers={"Authorization": f"Bearer {token}"})
    response = test_client.post(f"/registrations/{test_event.id}", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 400
    assert "User already registered for this event" in response.json()["detail"]

def test_register_for_full_event(test_client: TestClient, db: Session, normal_user: User, full_event: Event):
    # First user registers successfully
    other_user = create_user(db, "other@test.com")
    token1 = create_access_token(data={"sub": other_user.email})
    response1 = test_client.post(f"/registrations/{full_event.id}", headers={"Authorization": f"Bearer {token1}"})
    assert response1.status_code == 200

    # Second user (normal_user) fails to register
    token2 = create_access_token(data={"sub": normal_user.email})
    response2 = test_client.post(f"/registrations/{full_event.id}", headers={"Authorization": f"Bearer {token2}"})
    assert response2.status_code == 400
    assert "Event is full" in response2.json()["detail"]

def test_unregister_from_event_success(test_client: TestClient, db: Session, normal_user: User, test_event: Event):
    token = create_access_token(data={"sub": normal_user.email})
    test_client.post(f"/registrations/{test_event.id}", headers={"Authorization": f"Bearer {token}"})
    response = test_client.delete(f"/registrations/{test_event.id}", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert "Unregistered from event" in response.json()["message"]

def test_unregister_from_event_not_registered(test_client: TestClient, db: Session, normal_user: User, test_event: Event):
    token = create_access_token(data={"sub": normal_user.email})
    response = test_client.delete(f"/registrations/{test_event.id}", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 404
    assert "Registration not found" in response.json()["detail"]

def test_list_registrations_for_event_admin(test_client: TestClient, db: Session, admin_user: User, normal_user: User, test_event: Event):
    # normal_user registers for the event
    token_normal = create_access_token(data={"sub": normal_user.email})
    test_client.post(f"/registrations/{test_event.id}", headers={"Authorization": f"Bearer {token_normal}"})

    # admin lists registrations
    token_admin = create_access_token(data={"sub": admin_user.email})
    response = test_client.get(f"/registrations/event/{test_event.id}", headers={"Authorization": f"Bearer {token_admin}"})
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["user_id"] == normal_user.id

def test_list_registrations_for_event_non_admin(test_client: TestClient, db: Session, normal_user: User, test_event: Event):
    token = create_access_token(data={"sub": normal_user.email})
    response = test_client.get(f"/registrations/event/{test_event.id}", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 403
    assert "Not authorized" in response.json()["detail"]
