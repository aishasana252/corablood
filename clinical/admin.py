from django.contrib import admin
from .models import DonorWorkflow, QuestionnaireResponse, Question, VitalSigns, BloodDraw, LabResult, LabOrder, VitalLimit, Medication, DeferralReason, CollectionConfig

@admin.register(LabResult)
class LabResultAdmin(admin.ModelAdmin):
    list_display = ('workflow', 'test_name', 'result_value', 'is_abnormal', 'created_at')
    list_filter = ('is_abnormal', 'test_name')

@admin.register(LabOrder)
class LabOrderAdmin(admin.ModelAdmin):
    list_display = ('order_code', 'workflow', 'system', 'status', 'created_at')
    list_filter = ('system', 'status')

@admin.register(DonorWorkflow)
class WorkflowAdmin(admin.ModelAdmin):
    list_display = ('donor', 'status', 'created_at')
    list_filter = ('status',)

@admin.register(VitalSigns)
class VitalsAdmin(admin.ModelAdmin):
    list_display = ('workflow', 'hemoglobin', 'bp_systolic', 'passed')

@admin.register(BloodDraw)
class BloodDrawAdmin(admin.ModelAdmin):
    list_display = ('workflow', 'examiner', 'segment_number', 'created_at')

from django.forms import Textarea
from django.db import models

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('text_en', 'category', 'is_active', 'order')
    list_editable = ('is_active', 'order')
    list_filter = ('category', 'is_active')
    search_fields = ('text_en', 'text_ar')
    
    formfield_overrides = {
        models.CharField: {'widget': Textarea(attrs={'rows': 3, 'cols': 80, 'style': 'width: 90%;'})},
    }

@admin.register(VitalLimit)
class VitalLimitAdmin(admin.ModelAdmin):
    list_display = ('min_hemoglobin', 'min_weight_kg', 'max_temperature_c')
    # This prevents adding more than one instance
    def has_add_permission(self, request):
        if self.model.objects.exists():
            return False
        return super().has_add_permission(request)

@admin.register(CollectionConfig)
class CollectionConfigAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        if self.model.objects.exists():
            return False
        return super().has_add_permission(request)

@admin.register(Medication)
class MedicationAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'deferral_days', 'is_active')
    list_filter = ('category', 'is_active')
    search_fields = ('name', 'category')

@admin.register(DeferralReason)
class DeferralReasonAdmin(admin.ModelAdmin):
    list_display = ('code', 'reason_en', 'is_permanent', 'default_duration_days')
