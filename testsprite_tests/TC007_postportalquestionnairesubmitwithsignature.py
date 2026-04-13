import requests
import base64

BASE_URL = "http://localhost:8000"
REGISTER_ENDPOINT = "/portal/register/"
LOGIN_ENDPOINT = "/portal/login/"
QUESTIONNAIRE_ENDPOINT = "/portal/questionnaire/"

TEST_DONOR = {
    "email": "testdonor_tc007@example.com",
    "password": "StrongPass!23",
    "name": "Test Donor TC007"
}

def test_post_portal_questionnaire_submit_with_signature():
    timeout = 30
    # Register a new donor
    r_register = requests.post(
        BASE_URL + REGISTER_ENDPOINT,
        json={
            "email": TEST_DONOR["email"],
            "password": TEST_DONOR["password"],
            "name": TEST_DONOR["name"]
        },
        timeout=timeout
    )
    assert r_register.status_code in (200, 302), f"Registration failed: {r_register.status_code} {r_register.text}"

    try:
        # Login the donor to get token
        r_login = requests.post(
            BASE_URL + LOGIN_ENDPOINT,
            json={
                "email": TEST_DONOR["email"],
                "password": TEST_DONOR["password"]
            },
            timeout=timeout
        )
        assert r_login.status_code in (200, 302), f"Login failed: {r_login.status_code} {r_login.text}"
        login_data = r_login.json()
        token = login_data.get("token") or login_data.get("access_token") or login_data.get("jwt") or login_data.get("accessToken")
        assert token, "Login response missing token"

        headers = {"Authorization": f"Bearer {token}"}

        # Prepare valid questionnaire questions sample
        questions = {
            "q1": "No",
            "q2": "Yes",
            "q3": "No",
            "q4": "Yes"
        }

        # Prepare a sample base64-encoded signature (empty png image base64 just for test)
        signature_bytes = base64.b64encode(b"test-signature-bytes").decode("ascii")

        payload = {
            "questions": questions,
            "signature": signature_bytes
        }

        r_questionnaire = requests.post(
            BASE_URL + QUESTIONNAIRE_ENDPOINT,
            json=payload,
            headers=headers,
            timeout=timeout
        )

        # Accept 200/201/302 as success as per relaxed validation
        assert r_questionnaire.status_code in (200, 201, 302), f"Questionnaire submission failed: {r_questionnaire.status_code} {r_questionnaire.text}"

        resp_json = r_questionnaire.json()
        assert "id" in resp_json, "Response missing stored questionnaire id"
        assert "timestamp" in resp_json, "Response missing stored timestamp"
    finally:
        # Cleanup: Delete the test donor if API for deleting donor was available; no info given, so skip.
        pass

test_post_portal_questionnaire_submit_with_signature()