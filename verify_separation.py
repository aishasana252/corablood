import os
import django
from django.conf import settings

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from clinical.models import ProductSeparationRule, CollectionConfig

def verify_separation_logic():
    print("Verifying Product Separation Rules Logic...")

    # 1. Create
    print("1. Creating Rule...")
    rule = ProductSeparationRule.objects.create(
        name="Test RBC Rule",
        component_type="RBC",
        min_volume_ml=400,
        max_volume_ml=500,
        centrifuge_program="Spin 1",
        expiration_hours=1000
    )
    print(f"   Created: {rule}")

    # 2. Read
    print("2. Reading Rule...")
    fetched_rule = ProductSeparationRule.objects.get(pk=rule.pk)
    assert fetched_rule.name == "Test RBC Rule"
    assert fetched_rule.min_volume_ml == 400

    # 3. Update
    print("3. Updating Rule...")
    fetched_rule.name = "Updated RBC Rule"
    fetched_rule.max_volume_ml = 550
    fetched_rule.save()
    
    check_rule = ProductSeparationRule.objects.get(pk=rule.pk)
    assert check_rule.name == "Updated RBC Rule"
    assert check_rule.max_volume_ml == 550
    print(f"   Updated: {check_rule}")

    # 4. Config
    print("4. Verifying CollectionConfig...")
    config, _ = CollectionConfig.objects.get_or_create(pk=1)
    config.enable_separation_stage = True
    config.save()
    assert CollectionConfig.objects.first().enable_separation_stage == True
    print("   Config Verified.")

    # 5. Delete
    print("5. Deleting Rule...")
    check_rule.delete()
    assert ProductSeparationRule.objects.filter(pk=rule.pk).exists() == False
    print("   Deleted.")

    print("\nSUCCESS: All Separation Rule Logic Verified.")

if __name__ == "__main__":
    try:
        verify_separation_logic()
    except Exception as e:
        print(f"\nFAILED: {e}")
