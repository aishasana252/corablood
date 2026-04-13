
import os
import django
import sys
import json

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from django.urls import reverse

User = get_user_model()

def test_api():
    print("Initializing API Client...")
    client = APIClient()
    
    # Get a user (e.g. superuser or first user)
    user = User.objects.filter(is_superuser=True).first()
    if not user:
        user = User.objects.first()
        
    if user:
        print(f"Authenticating as: {user.username}")
        client.force_authenticate(user=user)
    else:
        print("WARNING: No users found in DB. Requesting as Anonymous.")

    url = '/donors/api/donors/'
    print(f"Requesting URL: {url}")
    
    try:
        response = client.get(url, format='json')
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            # DRF pagination structure check
            if 'results' in data:
                print(f"Results Count: {len(data['results'])}")
                print("First item sample:")
                if len(data['results']) > 0:
                    print(json.dumps(data['results'][0], indent=2))
                else:
                    print("List is empty.")
            else:
                 print("No 'results' key found. Raw list?")
                 print(f"Count: {len(data)}")
                 if len(data) > 0:
                     print("First item sample:")
                     print(json.dumps(data[0], indent=2))
        else:
            print("Response Error Content:")
            print(response.content.decode('utf-8'))
            
    except Exception as e:
        print(f"CRITICAL EXCEPTION: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_api()
