import os
import django
from django.conf import settings
from django.urls import get_resolver

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

print("Scanning URLs...")
url_patterns = get_resolver().url_patterns
for pattern in url_patterns:
    print(f"{pattern}")
    if hasattr(pattern, 'url_patterns'):
        for sub in pattern.url_patterns:
            print(f"  - {sub}")

from django.urls import reverse
try:
    print(f"Reverse 'questions-list': {reverse('questions-list')}")
except Exception as e:
    print(f"Reverse failed: {e}")
