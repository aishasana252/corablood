import requests
import uuid

BASE_URL = "http://localhost:8000"
TIMEOUT = 30


def test_postportalloginvaliddonorcredentials():
    register_url = f"{BASE_URL}/portal/register/"
    login_url = f"{BASE_URL}/portal/login/"

    # Create unique email for testing
    unique_email = f"testuser_{uuid.uuid4()}@example.com"
    password = "StrongPassword!123"
    name = "Test User"

    register_payload = {
        "email": unique_email,
        "password": password,
        "name": name
    }
    headers = {"Content-Type": "application/json"}

    try:
        # Register donor
        reg_response = requests.post(register_url, json=register_payload, headers=headers, timeout=TIMEOUT)
        assert reg_response.status_code in (200, 302), f"Unexpected registration status code: {reg_response.status_code}"

        # Login donor
        login_payload = {
            "email": unique_email,
            "password": password
        }
        login_response = requests.post(login_url, json=login_payload, headers=headers, timeout=TIMEOUT)
        assert login_response.status_code in (200, 302), f"Unexpected login status code: {login_response.status_code}"

        # Response should have JWT token
        # Accept either application/json or possible redirect with token in body
        try:
            json_resp = login_response.json()
        except ValueError:
            assert False, "Login response is not valid JSON"

        assert "token" in json_resp and isinstance(json_resp["token"], str) and json_resp["token"], "JWT token missing or invalid in login response"

    finally:
        # Attempt deletion if API supported donor deletion, but not specified. Skipping cleanup.
        pass


test_postportalloginvaliddonorcredentials()