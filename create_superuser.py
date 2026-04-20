import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

# --- Doctor Admin Account ---
username = 'doctor'
password = 'CoraBlood@2026'

if not User.objects.filter(username=username).exists():
    user = User.objects.create_superuser(username=username, email='doctor@corablood.com', password=password)
    user.role = 'Doctor'
    user.is_staff = True
    user.is_superuser = True
    user.can_access_dashboard = True
    user.can_access_donors = True
    user.can_access_donations = True
    user.can_access_settings = True
    user.can_access_inventory = True
    user.can_access_reports = True
    user.can_access_clinical = True
    user.can_access_orders = True
    user.can_access_ai = True
    user.save()
    print(f"Doctor admin '{username}' created with full access.")
else:
    print(f"User '{username}' already exists.")
