import requests

BASE_URL = "http://localhost:8000"
TIMEOUT = 30

admin_credentials = {
    "email": "admin@example.com",
    "password": "AdminPass123!"
}

def test_get_api_donations_fetch_workflow_admin():
    # Login as admin to get token
    login_url = f"{BASE_URL}/portal/login/"
    login_payload = {
        "email": admin_credentials["email"],
        "password": admin_credentials["password"]
    }
    headers = {"Content-Type": "application/json"}

    login_resp = requests.post(login_url, json=login_payload, headers=headers, timeout=TIMEOUT)
    assert login_resp.status_code in (200, 302), f"Admin login failed with status {login_resp.status_code}"
    # Try parse JWT token from response JSON, fallback to empty string
    try:
        token = login_resp.json().get("token") or login_resp.json().get("access_token") or ""
        assert token, "No token received from admin login"
    except Exception as e:
        assert False, f"Failed to parse login response JSON: {e}"

    auth_headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    # We have no given donation id. Create a donor, appointment, questionnaire, medication, then get donation id.
    donor_email = "testdonorworkflow@example.com"
    donor_password = "TestPass123!"
    donor_name = "Test Donor"

    try:
        # Register donor
        register_url = f"{BASE_URL}/portal/register/"
        register_payload = {
            "email": donor_email,
            "password": donor_password,
            "name": donor_name
        }
        reg_resp = requests.post(register_url, json=register_payload, headers=headers, timeout=TIMEOUT)
        assert reg_resp.status_code in (200, 302), f"Donor registration failed with status {reg_resp.status_code}"
        donor_id = None
        try:
            donor_id = reg_resp.json().get("id") or reg_resp.json().get("donor_id")
        except Exception:
            donor_id = None
        assert donor_id, "Donor ID not received in registration response"

        # Donor login to get token
        login_payload_donor = {"email": donor_email, "password": donor_password}
        login_resp_donor = requests.post(login_url, json=login_payload_donor, headers=headers, timeout=TIMEOUT)
        assert login_resp_donor.status_code in (200, 302), f"Donor login failed with status {login_resp_donor.status_code}"
        donor_token = None
        try:
            donor_token = login_resp_donor.json().get("token") or login_resp_donor.json().get("access_token")
        except Exception:
            donor_token = None
        assert donor_token, "Donor token not received after login"

        donor_auth_headers = {
            "Authorization": f"Bearer {donor_token}",
            "Content-Type": "application/json"
        }

        # Book appointment (minimal valid data)
        from datetime import date, datetime, time, timedelta

        appt_url = f"{BASE_URL}/portal/dashboard/"
        hospital_id = 1  # assume hospital with id 1 exists
        appt_date = date.today().isoformat()
        # Choose appointment time as now + 1 hour, rounded to hour
        appt_time = (datetime.now() + timedelta(hours=1)).strftime("%H:00")
        appt_payload = {
            "hospital_id": hospital_id,
            "appointment_date": appt_date,
            "appointment_time": appt_time
        }
        appt_resp = requests.post(appt_url, json=appt_payload, headers=donor_auth_headers, timeout=TIMEOUT)
        assert appt_resp.status_code in (200, 201, 302), f"Appointment booking failed with status {appt_resp.status_code}"

        appointment_id = None
        try:
            appointment_id = appt_resp.json().get("id") or appt_resp.json().get("appointment_id")
        except Exception:
            appointment_id = None
        assert appointment_id, "Appointment ID not received"

        # Submit medical questionnaire
        questionnaire_url = f"{BASE_URL}/portal/questionnaire/"
        questionnaire_payload = {
            "questions": {
                "q1": "Yes",
                "q2": "No"
            },
            # Simulate signature as base64 string
            "signature": "c2lnbmF0dXJlZGF0YQ=="
        }
        questionnaire_resp = requests.post(questionnaire_url, json=questionnaire_payload, headers=donor_auth_headers, timeout=TIMEOUT)
        assert questionnaire_resp.status_code in (200, 201, 302), f"Questionnaire submission failed with status {questionnaire_resp.status_code}"
        questionnaire_id = None
        try:
            questionnaire_id = questionnaire_resp.json().get("id") or questionnaire_resp.json().get("questionnaire_id")
        except Exception:
            questionnaire_id = None
        assert questionnaire_id, "Questionnaire ID not received"

        # Submit medication records
        medication_url = f"{BASE_URL}/portal/medication/"
        medication_payload = {
            "medications": [
                {
                    "name": "Aspirin",
                    "dose": "100mg",
                    "frequency": "Once daily",
                    "category": "Painkiller"
                }
            ]
        }
        medication_resp = requests.post(medication_url, json=medication_payload, headers=donor_auth_headers, timeout=TIMEOUT)
        assert medication_resp.status_code in (200, 201, 302), f"Medication submission failed with status {medication_resp.status_code}"
        medication_id = None
        try:
            medication_id = medication_resp.json().get("id") or medication_resp.json().get("medication_id")
        except Exception:
            medication_id = None
        assert medication_id, "Medication ID not received"

        # After these steps, assume a donation record exists linking these entities.
        # The API expects /api/donations/{id}/. It's implied donation id corresponds to appointment or combined record.
        # Since no direct donation create endpoint visible, we try appointment_id as donation id.

        donation_id = appointment_id

        # Fetch full donation workflow with admin token
        donation_url = f"{BASE_URL}/api/donations/{donation_id}/"
        donation_resp = requests.get(donation_url, headers=auth_headers, timeout=TIMEOUT)
        assert donation_resp.status_code == 200, f"Fetching donation workflow failed with status {donation_resp.status_code}"
        workflow_data = donation_resp.json()
        # Validate expected workflow data keys
        expected_keys = {"donor", "appointment", "questionnaire", "medications", "clinical_status"}
        assert expected_keys.issubset(workflow_data.keys()), f"Workflow data missing expected keys: {expected_keys - workflow_data.keys()}"

    finally:
        # Cleanup: delete donor resource (assuming DELETE /portal/donors/{id}/ exists)
        # or any API to delete registered donor
        # Since PRD does not specify delete endpoints, pass here.
        pass

test_get_api_donations_fetch_workflow_admin()