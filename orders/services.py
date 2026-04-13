from django.utils import timezone
from .models import BloodOrder, Crossmatch
from inventory.models import BloodComponent
from django.db import transaction

class OrderService:
    @staticmethod
    def create_order(data, user):
        return BloodOrder.objects.create(
            requester=user,
            **data
        )

    @staticmethod
    def find_compatible_units(order):
        """
        Find units that match blood group and component type.
        Prioritize Expiration (FIFO).
        """
        # Exact Match for V3 (Can add compatible lookup table later)
        target_group = order.patient_blood_group
        compat_groups = [target_group] 
        if target_group == 'AB+':
            compat_groups = ['AB+', 'A+', 'B+', 'O+', 'AB-', 'A-', 'B-', 'O-'] # Universal Receiver for Plasma? No, for RBC it's reverse.
            # Let's stick to Exact Match for Safety in Prototype V3 unless specified
            compat_groups = [target_group, 'O-'] # Safe fallback
            
        units = BloodComponent.objects.filter(
            component_type=order.component_type,
            status=BloodComponent.Status.AVAILABLE,
            blood_group__in=compat_groups
        ).order_by('expiration_date') # FIFO
        
        return units

    @staticmethod
    def perform_crossmatch(order, unit, user):
        # In reality, this is a physical lab test.
        # In System V3, we simulate the result recording.
        
        # Check compatibility logic (Simulation)
        is_compatible = True
        if order.patient_blood_group != unit.blood_group and unit.blood_group != 'O-':
             is_compatible = False
             
        xm = Crossmatch.objects.create(
            order=order,
            unit=unit,
            is_compatible=is_compatible,
            technician=user
        )
        
        if is_compatible:
            # Reserve the unit
            unit.status = BloodComponent.Status.RESERVED
            unit.save()
            
            order.status = BloodOrder.Status.CROSSMATCHING
            order.save()
            
        return xm

    @staticmethod
    def dispense_unit(crossmatch, user):
        if not crossmatch.is_compatible:
            raise ValueError("Cannot dispense incompatible unit")
            
        unit = crossmatch.unit
        unit.status = BloodComponent.Status.TRANSFUSED
        unit.save()
        
        order = crossmatch.order
        order.status = BloodOrder.Status.ISSUED # Or COMPLETED
        order.save()
        
        return unit
