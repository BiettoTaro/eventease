import requests
import time

BASE_URL = "http://backend:8000"
ADMIN_EMAIL = "admin@eventease.com"
ADMIN_PASSWORD = "Admin@123"

def wait_for_backend():
    for _ in range(30):
        try:
            r = requests.get(f"{BASE_URL}/health")
            if r.status_code == 200:
                print("Backend is ready")
                return True
        except Exception:
            pass
        print("Waiting for backend...")
        time.sleep(2)
    raise RuntimeError("Backend not available")

def login_admin():
    print("Logging in as admin...")
    resp = requests.post(
        f"{BASE_URL}/auth/login",
        data={  
            "username": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        }
    )
    resp.raise_for_status()
    data = resp.json()
    return data["access_token"]

if __name__ == "__main__":
    wait_for_backend()
    token = login_admin()
    print("Token acquired:", token[:20], "...")
