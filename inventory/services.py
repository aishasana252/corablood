from django.utils import timezone
from .models import BloodComponent
import uuid

class InventoryService:
    @staticmethod
    def separate_batch(workflow, components_list, user=None):
        """
        components_list = [{'type': 'PRBC', 'volume': 250}, {'type': 'FFP', 'volume': 200}]
        """
        # Clear existing components to prevent duplicates/allow re-submission
        BloodComponent.objects.filter(workflow=workflow).delete()
        
        created = []
        
        # Get base info
        draw = workflow.blood_draw
        base_serial = draw.segment_number
        blood_group = workflow.donor.blood_group # Fallback to donor group roughly
        # Sanitize: if blood group is 'UNKNOWN' or empty, use a safe placeholder
        if not blood_group or blood_group.upper() == 'UNKNOWN':
            blood_group = 'UNK'
        
        # Determine Expirations (Simple Rules)
        now = timezone.now()
        
        rules = {
            'PRBC': 35, # Days
            'PLT': 5,
            'FFP': 365,
            'CRYO': 365
        }

        for idx, comp in enumerate(components_list):
            c_type = comp.get('type')
            volume = comp.get('volume')
            
            days = rules.get(c_type, 35)
            expiry = now + timezone.timedelta(days=days)
            
            # Suffix serial: UNIT-1234 -> UNIT-1234-01
            unit_no = f"{base_serial}-{idx+1:02d}"
            
            # Parse storage_time string into proper time object
            storage_time_raw = comp.get('storage_time') or None
            storage_time_obj = None
            if storage_time_raw:
                from datetime import datetime
                for fmt in ('%I:%M %p', '%H:%M', '%I:%M%p', '%H:%M:%S'):
                    try:
                        storage_time_obj = datetime.strptime(storage_time_raw.strip(), fmt).time()
                        break
                    except ValueError:
                        continue

            component = BloodComponent.objects.create(
                workflow=workflow,
                component_type=c_type,
                unit_number=unit_no,
                segment_number=f"SEG-{idx+1}",
                blood_group=blood_group,
                volume_ml=volume,
                status=BloodComponent.Status.QUARANTINE,
                expiration_date=expiry,
                location="Quarantine Fridge",
                visual_inspection=comp.get('visual_inspection', False),
                room_temp_check=comp.get('room_temp', False),
                storage_time_after_prep=storage_time_obj,
                notes=comp.get('notes', '')
            )
            created.append(component)
            
        return created

    @staticmethod
    def release_components(workflow, passed=True):
        components = BloodComponent.objects.filter(workflow=workflow)
        for c in components:
            if passed:
                c.status = BloodComponent.Status.AVAILABLE
                c.location = "Main Stock Fridge"
            else:
                c.status = BloodComponent.Status.DISCARDED
                c.location = "Biohazard Disposal"
            c.save()
