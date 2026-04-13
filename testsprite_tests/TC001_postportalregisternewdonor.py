import requests
import uuid

BASE_URL = "http://localhost:8000"
REGISTER_ENDPOINT = "/portal/register/"
TIMEOUT = 30

def test_postportalregisternewdonor():
    url = BASE_URL + REGISTER_ENDPOINT
    # Create unique email to avoid duplicates
    unique_email = f"testuser_{uuid.uuid4().hex[:8]}@example.com"
    payload = {
        "email": unique_email,
        "password": "SecurePass123!",
        "name": "Test User"
    }
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=TIMEOUT)
    except requests.RequestException as e:
        assert False, f"Request failed: {e}"

    # Acceptable success status codes are 200 or 302 per instructions
    assert response.status_code in (200, 302), f"Expected status 200 or 302 but got {response.status_code}"

    try:
        data = response.json()
    except ValueError:
        assert False, "Response is not valid JSON"

    # The response should include donor id
    assert "id" in data, "Response JSON does not contain donor id"

test_postportalregisternewdonor()
