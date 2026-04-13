import requests
import uuid

BASE_URL = "http://localhost:8000"
TIMEOUT = 30

def postportalmedicationsubmitvalid():
    # Step 1: Register a new donor user to use for this test (to ensure independent test environment)
    register_url = f"{BASE_URL}/portal/register/"
    user_email = f"testuser_{uuid.uuid4().hex[:8]}@example.com"
    user_password = "ValidPass123!"
    register_payload = {
        "email": user_email,
        "password": user_password,
        "name": "Test User"
    }
    register_headers = {"Content-Type": "application/json"}
    try:
        register_response = requests.post(register_url, json=register_payload, headers=register_headers, timeout=TIMEOUT)
        assert register_response.status_code in (200, 302), f"Registration failed with status {register_response.status_code}"

        # Step 2: Log in to get JWT token
        login_url = f"{BASE_URL}/portal/login/"
        login_payload = {
            "email": user_email,
            "password": user_password
        }
        login_headers = {"Content-Type": "application/json"}
        login_response = requests.post(login_url, json=login_payload, headers=login_headers, timeout=TIMEOUT)
        assert login_response.status_code in (200, 302), f"Login failed with status {login_response.status_code}"
        login_json = login_response.json()
        token = login_json.get("token") or login_json.get("access") or login_json.get("jwt") or login_json.get("access_token")
        assert token, f"No token received in login response: {login_json}"

        # Step 3: Submit categorized medication records with valid token and correct payload
        medication_url = f"{BASE_URL}/portal/medication/"
        medication_payload = {
            "medications": [
                {"name": "Aspirin", "dose": "81 mg", "frequency": "Once daily", "category": "Antiplatelet"},
                {"name": "Lisinopril", "dose": "10 mg", "frequency": "Once daily", "category": "Antihypertensive"}
            ]
        }
        medication_headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        }
        medication_response = requests.post(medication_url, json=medication_payload, headers=medication_headers, timeout=TIMEOUT)
        # Expecting 200 or 302 status indicates successful medication record creation per PRD
        assert medication_response.status_code in (200, 302), f"Expected 200 or 302 but got {medication_response.status_code}"
        med_json = medication_response.json()
        # Validate that a medication record id is returned in response
        med_id = med_json.get("id") or med_json.get("medication_record_id") or med_json.get("medication_id")
        assert med_id is not None, f"Medication record ID not found in response: {med_json}"

    finally:
        # Cleanup: No explicit delete endpoint mentioned for medication records,
        # and since medications are tied to user, deleting user is best cleanup if possible.
        # No info about user deletion API, so skipping cleanup of user and medication for now.
        pass

postportalmedicationsubmitvalid()
