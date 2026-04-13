import requests
import uuid

BASE_URL = "http://localhost:8000"
REGISTER_ENDPOINT = f"{BASE_URL}/portal/register/"
TIMEOUT = 30
HEADERS = {'Content-Type': 'application/json'}

def test_postportalregisterduplicateemail():
    # Generate a unique email for initial registration
    unique_email = f"testuser_{uuid.uuid4().hex[:8]}@example.com"
    password = "SecurePass123!"
    name = "Test User"

    register_payload = {
        "email": unique_email,
        "password": password,
        "name": name
    }

    # First registration attempt should succeed (200 or 302)
    response_first = requests.post(REGISTER_ENDPOINT, json=register_payload, headers=HEADERS, timeout=TIMEOUT)
    assert response_first.status_code in (200, 302), f"Initial registration failed: {response_first.status_code} {response_first.text}"

    # Second registration attempt with the same email should fail with 400 and 'email already exists' error
    response_second = requests.post(REGISTER_ENDPOINT, json=register_payload, headers=HEADERS, timeout=TIMEOUT)
    assert response_second.status_code == 400, f"Expected 400 for duplicate email, got {response_second.status_code}"
    try:
        resp_json = response_second.json()
    except ValueError:
        resp_json = {}
    error_message = None
    if isinstance(resp_json, dict):
        # Check common patterns for error message
        if 'email' in resp_json:
            # often validation errors are returned keyed by field name
            errors = resp_json.get('email')
            if isinstance(errors, list) and errors:
                error_message = errors[0].lower()
            elif isinstance(errors, str):
                error_message = errors.lower()
        elif 'detail' in resp_json and isinstance(resp_json['detail'], str):
            error_message = resp_json['detail'].lower()
        else:
            # fallback: search all strings in response for error message
            for v in resp_json.values():
                if isinstance(v, str):
                    error_message = v.lower()
                    break
    assert error_message is not None and "email already exists" in error_message, "Error message does not mention 'email already exists'"

test_postportalregisterduplicateemail()
