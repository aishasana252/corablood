import requests

BASE_URL = "http://localhost:8000"
REGISTER_URL = f"{BASE_URL}/portal/register/"
LOGIN_URL = f"{BASE_URL}/portal/login/"
DASHBOARD_URL = f"{BASE_URL}/portal/dashboard/"

TEST_DONOR_EMAIL = "testdonor_conflict@example.com"
TEST_DONOR_PASSWORD = "StrongP@ssword123"
TEST_DONOR_NAME = "Test Donor Conflict"

def test_postportaldashboardconflictingappointmenttime():
    headers_json = {"Content-Type": "application/json"}
    # Register donor
    try:
        register_resp = requests.post(
            REGISTER_URL,
            json={"email": TEST_DONOR_EMAIL, "password": TEST_DONOR_PASSWORD, "name": TEST_DONOR_NAME},
            headers=headers_json,
            timeout=30,
        )
        assert register_resp.status_code in (200, 302), f"Registration failed: {register_resp.text}"

        # Login donor
        login_resp = requests.post(
            LOGIN_URL,
            json={"email": TEST_DONOR_EMAIL, "password": TEST_DONOR_PASSWORD},
            headers=headers_json,
            timeout=30,
        )
        assert login_resp.status_code in (200, 302), f"Login failed: {login_resp.text}"
        login_data = login_resp.json()
        token = login_data.get("token") or login_data.get("access") or login_data.get("jwt")
        assert token, "Token not found in login response"

        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

        # Book initial appointment (should succeed)
        appointment_data_1 = {
            "hospital_id": 1,
            "appointment_date": "2026-12-01",
            "appointment_time": "10:00"
        }
        book_resp_1 = requests.post(DASHBOARD_URL, json=appointment_data_1, headers=headers, timeout=30)
        assert book_resp_1.status_code in (200, 201, 302), f"First appointment booking failed: {book_resp_1.text}"
        # Confirm appointment id exists
        appt_1_data = book_resp_1.json()
        appt_1_id = appt_1_data.get("id")
        assert appt_1_id is not None, "First appointment id missing"

        # Attempt to book a conflicting appointment (same date and time)
        appointment_data_conflict = {
            "hospital_id": 1,
            "appointment_date": "2026-12-01",
            "appointment_time": "10:00"
        }
        book_resp_2 = requests.post(DASHBOARD_URL, json=appointment_data_conflict, headers=headers, timeout=30)

        # Expect 409 Conflict with 'time slot unavailable' error message
        assert book_resp_2.status_code == 409, f"Expected 409 Conflict but got {book_resp_2.status_code}"
        error_resp = book_resp_2.json()
        error_message = error_resp.get("error") or error_resp.get("detail") or error_resp.get("message", "")
        assert "time slot unavailable" in error_message.lower(), f"Unexpected error message: {error_message}"

    finally:
        # Cleanup: No delete endpoint specified for appointments or donors; test environment should handle data rollback.
        pass

test_postportaldashboardconflictingappointmenttime()