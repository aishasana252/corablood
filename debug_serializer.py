
import os
import django
import sys

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from donors.models import Donor
from donors.serializers import DonorSerializer
from clinical.models import DonorWorkflow

def test_serializer():
    print("Testing DonorSerializer...")
    donors = Donor.objects.all()
    print(f"Total Donors in DB: {donors.count()}")
    
    for donor in donors:
        print(f"--- Donor: {donor.full_name} (ID: {donor.id}) ---")
        workflows = donor.workflows.all()
        print(f"  Workflows count: {workflows.count()}")
        for wf in workflows:
            print(f"    - WF ID: {wf.id}, Status: {wf.status}")
        
        # Test Serializer Logic
        active = donor.workflows.exclude(status__in=['COMPLETED', 'DEFERRED']).last()
        print(f"  Serializer Active Logic result: {active.status if active else 'None'}")
        print("------------------------------------------------")
        print("------------------------------------------------")


if __name__ == '__main__':
    test_serializer()
