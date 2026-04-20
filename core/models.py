from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):

    # Free text role (Admin can write any role title)
    role = models.CharField(
        max_length=100,
        blank=True,
        default='',
        verbose_name='Role / Job Title',
        help_text='e.g. Doctor, Nurse, Lab Technician, Receptionist'
    )

    # Module Access Permissions (Checkboxes)
    can_access_dashboard   = models.BooleanField(default=False, verbose_name='Dashboard')
    can_access_donors      = models.BooleanField(default=False, verbose_name='Main Navigation')
    can_access_donations   = models.BooleanField(default=False, verbose_name='Donation Process')
    can_access_settings    = models.BooleanField(default=False, verbose_name='Administration')
    can_access_inventory   = models.BooleanField(default=False, verbose_name='Inventory & Labs')
    can_access_reports     = models.BooleanField(default=False, verbose_name='Reports')
    can_access_clinical    = models.BooleanField(default=False, verbose_name='Lab Result')
    can_access_orders      = models.BooleanField(default=False, verbose_name='Blood Order Process / Patient Services')
    can_access_ai          = models.BooleanField(default=False, verbose_name='AI Manager')

    def __str__(self):
        return f"{self.username} ({self.role or 'No Role'})"

class SystemSettings(models.Model):
    # Registration Rules
    donor_id_length = models.IntegerField(default=10, help_text="Required length for National ID")
    donor_phone_length = models.IntegerField(default=10, help_text="Required length for Phone Number")
    donor_phone_prefix = models.CharField(max_length=5, default="0", help_text="Required prefix for Phone Number")
    donor_min_age = models.IntegerField(default=18, help_text="Minimum allowed age for donors")
    donor_max_age = models.IntegerField(default=60, help_text="Maximum allowed age for donors")

    class Meta:
        verbose_name = "Global System Rules"
        verbose_name_plural = "Global System Rules"

    def save(self, *args, **kwargs):
        self.pk = 1 # Force singleton
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        return obj

    def __str__(self):
        return "Registration & System Rules"

