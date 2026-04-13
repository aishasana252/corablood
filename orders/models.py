from django.db import models
from core.models import User
from inventory.models import BloodComponent

class BloodOrder(models.Model):
    class Urgency(models.TextChoices):
        ROUTINE = 'ROUTINE', 'Routine'
        URGENT = 'URGENT', 'Urgent'
        EMERGENCY = 'EMERGENCY', 'Life Threatening (Emergency)'

    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pending Request'
        CROSSMATCHING = 'CROSSMATCHING', 'Crossmatching'
        ISSUED = 'ISSUED', 'Issued/Dispensed'
        COMPLETED = 'COMPLETED', 'Completed/Transfused'
        CANCELLED = 'CANCELLED', 'Cancelled'

    # Patient Info
    patient_mrn = models.CharField(max_length=50, help_text="Medical Record Number")
    patient_full_name = models.CharField(max_length=200)
    patient_blood_group = models.CharField(max_length=5) # A+, O-, etc.
    hospital_ward = models.CharField(max_length=100)
    
    # Request Details
    component_type = models.CharField(max_length=10, choices=BloodComponent.Type.choices)
    units_requested = models.IntegerField(default=1)
    urgency = models.CharField(max_length=20, choices=Urgency.choices, default=Urgency.ROUTINE)
    required_date = models.DateField(null=True, blank=True)
    
    # Workflow
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    requester = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='requested_orders')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order #{self.id} - {self.patient_full_name} ({self.units_requested}x {self.component_type})"

class Crossmatch(models.Model):
    order = models.ForeignKey(BloodOrder, on_delete=models.CASCADE, related_name='crossmatches')
    unit = models.ForeignKey(BloodComponent, on_delete=models.CASCADE, related_name='crossmatches')
    
    is_compatible = models.BooleanField(default=False)
    technician = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    tested_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('order', 'unit')
