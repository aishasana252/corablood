from django.db import models
from django.utils import timezone
from core.models import User
from clinical.models import DonorWorkflow

class BloodComponent(models.Model):
    class Type(models.TextChoices):
        WB = 'WB', 'Whole Blood'
        PRBC = 'PRBC', 'Packed Red Blood Cells'
        FFP = 'FFP', 'Fresh Frozen Plasma'
        PLT = 'PLT', 'Platelets'
        CRYO = 'CRYO', 'Cryoprecipitate'
        APHERESIS = 'APHERESIS', 'Apheresis Component'

    class Status(models.TextChoices):
        QUARANTINE = 'QUARANTINE', 'Quarantine (Untested)'
        AVAILABLE = 'AVAILABLE', 'Available'
        RESERVED = 'RESERVED', 'Reserved'
        TRANSFUSED = 'TRANSFUSED', 'Transfused'
        EXPIRED = 'EXPIRED', 'Expired'
        DISCARDED = 'DISCARDED', 'Discarded'

    # Link to origin workflow
    workflow = models.ForeignKey(DonorWorkflow, on_delete=models.CASCADE, related_name='components')
    
    # Core Data
    component_type = models.CharField(max_length=10, choices=Type.choices)
    unit_number = models.CharField(max_length=50, unique=True, help_text="e.g. UNIT-12345-01")
    segment_number = models.CharField(max_length=50, blank=True)
    
    # Clinical Data (Cached from Donor/Lab for query speed)
    blood_group = models.CharField(max_length=10, db_index=True)  # A+, O-, etc. (max_length=10 matches Donor model)
    volume = models.IntegerField(default=0)  # Standardized field name
    
    # Labeling Tracking
    is_labeled = models.BooleanField(default=False)
    label_printed_at = models.DateTimeField(null=True, blank=True)
    
    # Supply Chain
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.QUARANTINE)
    location = models.CharField(max_length=100, default="Processing Fridge")
    
    # Timestamps & Tracking
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_components')
    modified_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='modified_components')
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_components')
    manufactured_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    expiration_date = models.DateTimeField()
    
    # Separation Checks
    visual_inspection = models.BooleanField(default=False, verbose_name="Visual Inspection")
    bacterial_contamination = models.CharField(max_length=50, default='None', verbose_name="Bacterial Contamination")
    room_temp_check = models.BooleanField(default=False, verbose_name="Room Temperature Check")
    storage_time_after_prep = models.TimeField(null=True, blank=True, verbose_name="Storage Time After Preparation")
    notes = models.TextField(blank=True, null=True, verbose_name="Notes")
    
    def __str__(self):
        return f"{self.unit_number} ({self.component_type} {self.blood_group})"

    def save(self, *args, **kwargs):
        # Auto-calculate expiration if not set? 
        # For V3, we assume service calculates correct expiration logic
        super().save(*args, **kwargs)

class SeparationConfig(models.Model):
    """
    Singleton model for Separation/Processing Settings.
    """
    enable_auto_separation = models.BooleanField(default=True, help_text="Automatically create components upon collection completion?")
    default_components = models.JSONField(default=list, help_text="List of component types to create by default e.g. ['PRBC', 'FFP']")
    
    # Expiration Defaults (Days)
    expiration_days_prbc = models.IntegerField(default=35)
    expiration_days_ffp = models.IntegerField(default=365)
    expiration_days_plt = models.IntegerField(default=5)
    
    def save(self, *args, **kwargs):
        if not self.pk and SeparationConfig.objects.exists():
            return SeparationConfig.objects.first()
        return super(SeparationConfig, self).save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        return obj

    class Meta:
        verbose_name_plural = "Separation Settings"
