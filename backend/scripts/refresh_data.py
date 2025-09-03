import time
import requests

BASE_URL = "http://backend:8000"
ADMIN_EMAIL = "admin@eventease.com"
ADMIN_PASSWORD = "Admin@123"

def wait_for_backend():
    """Wait until backend is ready"""
    for _ in range(30):
        try:
            r = requests.get(f"{BASE_URL}/docs")
            if r.status_code == 200:
                return True
        except:
            pass
        time.sleep(2)
    raise RuntimeError("Backend did not become ready in time")

def login_admin():
    resp = requests.post(
        f"{BASE_URL}/auth/login",
        json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD},
    )
    resp.raise_for_status()
    data = resp.json()
    return data["access_token"]


def refresh_data(token):
    headers = {"Authorization": f"Bearer {token}"}
    for path in ["/news/refresh", "/events/refresh"]:
        r = requests.post(f"{BASE_URL}{path}", headers=headers)
        print(path, r.status_code, r.text)

if __name__ == "__main__":
    print("Waiting for backend...")
    wait_for_backend()
    print("Logging in as admin...")
    token = login_admin()
    print("Refreshing news & events...")
    refresh_data(token)
    print("Done")
