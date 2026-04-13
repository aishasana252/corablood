import requests
import uuid
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8000"
TIMEOUT = 30

def test_postportaldashboardbookappointment():
    # Generate random user details for registration
    random_suffix = str(uuid.uuid4())[:8]
    email = f"testuser_{random_suffix}@example.com"
    password = "TestPass123!"
    name = "Test User"
    
    headers = {
        "Content-Type": "application/json"
    }
    
    # Register new donor
    reg_payload = {
        "email": email,
        "password": password,
        "name": name
    }

    reg_response = requests.post(
        f"{BASE_URL}/portal/register/",
        json=reg_payload,
        headers=headers,
        timeout=TIMEOUT,
        allow_redirects=False  # handle 302 redirect
    )
    assert reg_response.status_code in (200, 302), f"Registration failed: {reg_response.status_code}, {reg_response.text}"

    # Login donor to get JWT token
    login_payload = {
        "email": email,
        "password": password
    }
    login_response = requests.post(
        f"{BASE_URL}/portal/login/",
        json=login_payload,
        headers=headers,
        timeout=TIMEOUT,
        allow_redirects=False
    )
    assert login_response.status_code in (200, 302), f"Login failed: {login_response.status_code}, {login_response.text}"
    try:
        token = login_response.json().get("token")
    except Exception:
        token = None
    assert token and isinstance(token, str), f"Token not found or invalid in login response: {login_response.text}"
    
    auth_headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }

    # Prepare appointment details
    # Use hospital_id=1 (assuming it exists)
    appointment_date = (datetime.utcnow() + timedelta(days=2)).date().isoformat()
    appointment_time = "14:00"  # 2 PM

    appointment_payload = {
        "hospital_id": 1,
        "appointment_date": appointment_date,
        "appointment_time": appointment_time
    }
    
    appointment_response = requests.post(
        f"{BASE_URL}/portal/dashboard/",
        json=appointment_payload,
        headers=auth_headers,
        timeout=TIMEOUT,
        allow_redirects=False
    )
    
    # The PRD states 200/302 on success; but test title mentions 201, so accept 201 also
    assert appointment_response.status_code in (200, 201, 302), \
        f"Appointment booking failed: {appointment_response.status_code}, {appointment_response.text}"
    
    try:
        appointment_data = appointment_response.json()
    except Exception:
        appointment_data = None
    
    assert appointment_data and "id" in appointment_data, f"Appointment confirmation or id missing: {appointment_response.text}"
    appointment_id = appointment_data.get("id")
    assert appointment_id and (isinstance(appointment_id, int) or isinstance(appointment_id, str)), "Invalid appointment id"
    
    # Cleanup: (No direct endpoint documented to delete appointment, so just pass)
    # If needed, donor deletion could be implemented, but not requested and no delete endpoint documented

test_postportaldashboardbookappointment()