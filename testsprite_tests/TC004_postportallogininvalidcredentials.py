import requests

BASE_URL = "http://localhost:8000"
TIMEOUT = 30

def test_postportallogininvalidcredentials():
    url = f"{BASE_URL}/portal/login/"
    headers = {"Content-Type": "application/json"}
    # Using credentials that are assumed invalid (not registered)
    payload = {
        "email": "invaliduser@example.com",
        "password": "WrongPassword123!"
    }
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=TIMEOUT)
    except requests.RequestException as e:
        assert False, f"Request failed: {e}"

    # The expected response code for invalid credentials is 401 Unauthorized
    assert response.status_code == 401, f"Expected status 401, got {response.status_code}"
    # Optionally, verify error message in response JSON if available
    try:
        json_resp = response.json()
        # The error message content is not explicitly specified, so relax check to existence of some error key or message
        assert any(k in json_resp for k in ['error', 'detail', 'message']), "Expected error detail in response"
    except ValueError:
        # response body might not be JSON
        pass

test_postportallogininvalidcredentials()