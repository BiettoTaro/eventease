from app.db.database import SessionLocal
from app.models.user import User
from app.utils.security import get_password_hash


def seed_admin():
    db = SessionLocal()
    
    # Check if admin already exists
    admin_email = "admin@eventease.com"
    existing = db.query(User).filter(User.email == admin_email).first()
    if existing:
        return
    
    # Create admin user
    admin = User(
        email=admin_email,
        name="Admin",
        password_hash=get_password_hash("Admin@123"),
        is_admin=True,
        city="London",
        country="UK"
    )
    db.add(admin)
    db.commit()
    print(f"Admin user seeded successfully: {admin_email} / Admin@123")

if __name__ == "__main__":
    seed_admin()

        
    