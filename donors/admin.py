from django.contrib import admin
from .models import Donor, Hospital, DonorAppointment

@admin.register(Hospital)
class HospitalAdmin(admin.ModelAdmin):
    list_display = ('name', 'address', 'is_active', 'created_at')
    search_fields = ('name', 'address')
    list_filter = ('is_active',)

@admin.register(DonorAppointment)
class DonorAppointmentAdmin(admin.ModelAdmin):
    list_display = ('donor', 'hospital', 'appointment_date', 'status')
    list_filter = ('status', 'hospital', 'appointment_date')
    search_fields = ('donor__full_name', 'hospital__name')

@admin.register(Donor)
class DonorAdmin(admin.ModelAdmin):
    list_display = ('national_id', 'full_name', 'blood_group', 'mobile', 'deferral_status')
    search_fields = ('national_id', 'full_name', 'mobile')
    list_filter = ('blood_group', 'gender', 'deferral_status')
