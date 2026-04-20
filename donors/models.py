from django.db import models
from django.utils.translation import gettext_lazy as _
from core.models import User

class Nationality(models.Model):
    name_en = models.CharField(max_length=100, unique=True, verbose_name=_("Name (English)"))
    name_ar = models.CharField(max_length=100, verbose_name=_("Name (Arabic)"))
    is_active = models.BooleanField(default=True)
    is_default = models.BooleanField(default=False)
    order = models.IntegerField(default=0)

    class Meta:
        verbose_name_plural = "Nationalities"
        ordering = ['order', 'name_en']

    def __str__(self):
        return f"{self.name_en} / {self.name_ar}"

class Donor(models.Model):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
    ]
    
    BLOOD_GROUP_CHOICES = [
        ('A+', 'A+'), ('A-', 'A-'),
        ('B+', 'B+'), ('B-', 'B-'),
        ('AB+', 'AB+'), ('AB-', 'AB-'),
        ('O+', 'O+'), ('O-', 'O-'),
        ('UNKNOWN', 'Unknown'),
    ]

    # Identification
    national_id = models.CharField(max_length=20, unique=True, verbose_name=_("National ID / Iqama"))
    full_name = models.CharField(max_length=255, verbose_name=_("Full Name"))
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    
    # Demographics
    date_of_birth = models.DateField(verbose_name=_("Date of Birth"))
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    nationality = models.CharField(max_length=100, default='Saudi Arabia')
    mobile = models.CharField(max_length=20, verbose_name=_("Mobile Number"), db_index=True)
    email = models.EmailField(blank=True, null=True, verbose_name=_("Email Address"), db_index=True)
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='donor_profile')
    
    # Clinical Info
    blood_group = models.CharField(max_length=10, choices=BLOOD_GROUP_CHOICES, default='UNKNOWN')
    last_donation_date = models.DateField(null=True, blank=True)
    deferral_status = models.BooleanField(default=False, help_text=_("Is currently deferred?"))
    deferral_reason = models.TextField(blank=True, null=True)
    deferral_end_date = models.DateField(null=True, blank=True)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='registered_donors')

    def __str__(self):
        return f"{self.full_name} ({self.national_id})"
    
    class Meta:
        indexes = [
            models.Index(fields=['national_id']),
            models.Index(fields=['full_name']),
            models.Index(fields=['mobile']),
            models.Index(fields=['created_at']),
        ]

    def calculate_age(self):

        import datetime
        if not self.date_of_birth:
            return 0
        today = datetime.date.today()
        return today.year - self.date_of_birth.year - ((today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))

    @property
    def is_eligible(self):
        """
        Calculates if the donor is currently eligible based on deferral status and date.
        """
        import datetime
        if self.deferral_status:
            return False
        
        if self.deferral_end_date and self.deferral_end_date > datetime.date.today():
            return False
            
        return True

    @property
    def next_eligible_date(self):
        """
        Alias for deferral_end_date to match template usage.
        """
        return self.deferral_end_date

class DonorDeferral(models.Model):
    class Type(models.TextChoices):
        TEMPORARY = 'TEMPORARY', 'Temporary'
        PERMANENT = 'PERMANENT', 'Permanent'

    donor = models.ForeignKey(Donor, on_delete=models.CASCADE, related_name='deferrals')
    workflow = models.ForeignKey('clinical.DonorWorkflow', on_delete=models.SET_NULL, null=True, blank=True, related_name='deferrals_created')
    
    reason = models.CharField(max_length=200, verbose_name=_("Title / Reason"))
    deferral_type = models.CharField(max_length=20, choices=Type.choices, default=Type.TEMPORARY)
    
    # Optional fields from screenshot
    donor_value = models.CharField(max_length=100, blank=True, null=True)
    reference_range = models.CharField(max_length=100, blank=True, null=True)
    
    start_date = models.DateField(auto_now_add=True)
    end_date = models.DateField(null=True, blank=True) # If null, indefinite or until manually removed? Or assume permanent means infinite.
    days_blocked = models.IntegerField(default=0, help_text="Number of days blocked")
    
    is_active = models.BooleanField(default=True)
    
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.donor.full_name} - {self.reason}"


class Hospital(models.Model):
    name = models.CharField(max_length=200, unique=True, verbose_name=_("Hospital Name"))
    address = models.TextField(blank=True, null=True, verbose_name=_("Address"))
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Hospital / Collection Center"
        verbose_name_plural = "Hospitals / Collection Centers"

    def __str__(self):
        return self.name

class DonorAppointment(models.Model):
    donor = models.ForeignKey(Donor, on_delete=models.CASCADE, related_name='appointments')
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE, related_name='appointments', null=True)
    hospital_branch = models.CharField(max_length=200, verbose_name=_("Hospital Branch"), blank=True, null=True) # Kept for legacy compatibility
    appointment_date = models.DateField(verbose_name=_("Appointment Date"), db_index=True)
    appointment_time = models.TimeField(verbose_name=_("Appointment Time"))
    
    DONATION_TYPES = [
        ('WHOLE_BLOOD', 'Whole Blood'),
        ('APHERESIS', 'Apheresis (Platelets/Plasma)'),
    ]
    donation_type = models.CharField(max_length=20, choices=DONATION_TYPES, default='WHOLE_BLOOD')
    blood_group = models.CharField(max_length=10, choices=Donor.BLOOD_GROUP_CHOICES, default='UNKNOWN')
    
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('CONFIRMED', 'Confirmed'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING', db_index=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        branch = self.hospital.name if self.hospital else self.hospital_branch
        return f"{self.donor.full_name} - {branch} - {self.appointment_date}"
