import requests

BASE_URL = "http://localhost:8000"
REGISTER_URL = f"{BASE_URL}/portal/register/"
LOGIN_URL = f"{BASE_URL}/portal/login/"
QUESTIONNAIRE_URL = f"{BASE_URL}/portal/questionnaire/"

TIMEOUT = 30

def test_postportalquestionnairemissingsignature():
    # Step 1: Register a new donor
    donor_email = "testuser_tc008@example.com"
    donor_password = "StrongPass!23"
    donor_name = "Test User TC008"
    register_payload = {
        "email": donor_email,
        "password": donor_password,
        "name": donor_name
    }
    try:
        reg_resp = requests.post(REGISTER_URL, json=register_payload, timeout=TIMEOUT)
        assert reg_resp.status_code in (200, 302), f"Unexpected register status: {reg_resp.status_code}"
        
        # Step 2: Login to get JWT token
        login_payload = {
            "email": donor_email,
            "password": donor_password
        }
        login_resp = requests.post(LOGIN_URL, json=login_payload, timeout=TIMEOUT)
        assert login_resp.status_code in (200, 302), f"Unexpected login status: {login_resp.status_code}"
        login_json = login_resp.json()
        token = login_json.get("token") or login_json.get("access_token") or login_json.get("jwt")
        assert token, "Login response missing token"
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        # Step 3: Submit questionnaire with missing 'signature' field
        questionnaire_payload = {
            "questions": {
                "q1": "yes",
                "q2": "no",
                "q3": "sometimes"
            }
            # signature field intentionally omitted
        }
        q_resp = requests.post(QUESTIONNAIRE_URL, headers=headers, json=questionnaire_payload, timeout=TIMEOUT)
        assert q_resp.status_code == 400, f"Expected 400 Bad Request but got {q_resp.status_code}"
        
        q_json = q_resp.json()
        error_message = q_json.get("error") or q_json.get("message") or ""
        assert "missing signature" in error_message.lower(), f"Expected 'missing signature' error but got: {error_message}"
    finally:
        # Cleanup not required as this donor is test isolated; if deletion endpoint existed, would delete here
        pass

test_postportalquestionnairemissingsignature()