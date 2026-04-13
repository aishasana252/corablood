from django.contrib import admin
from .models import BloodComponent, SeparationConfig

@admin.register(BloodComponent)
class BloodComponentAdmin(admin.ModelAdmin):
    list_display = ('unit_number', 'component_type', 'blood_group', 'status', 'location', 'expiration_date')
    list_filter = ('component_type', 'blood_group', 'status', 'location')
    search_fields = ('unit_number',)

@admin.register(SeparationConfig)
class SeparationConfigAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        if self.model.objects.exists():
            return False
        return super().has_add_permission(request)
