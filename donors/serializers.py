from rest_framework import serializers
from .models import Donor, DonorDeferral

class DonorDeferralSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    
    class Meta:
        model = DonorDeferral
        fields = '__all__'
        read_only_fields = ['created_by', 'created_at']

class DonorSerializer(serializers.ModelSerializer):
    deferrals = DonorDeferralSerializer(many=True, read_only=True)
    active_workflow_id = serializers.SerializerMethodField()
    active_workflow_status = serializers.SerializerMethodField()
    
    class Meta:
        model = Donor
        fields = ['id', 'national_id', 'full_name', 'date_of_birth', 'gender', 'nationality', 'mobile', 'blood_group', 'last_donation_date', 'deferral_status', 'deferral_reason', 'deferral_end_date', 'created_at', 'updated_at', 'created_by', 'deferrals', 'active_workflow_id', 'active_workflow_status', 'is_eligible']

    def get_active_workflow_id(self, obj):
        # Efficiently check for active workflow (not completed/deferred)
        # Using the related name 'workflows' from DonorWorkflow model
        active = obj.workflows.exclude(status__in=['COMPLETED', 'DEFERRED']).last()
        return active.id if active else None

    def get_active_workflow_status(self, obj):
        active = obj.workflows.exclude(status__in=['COMPLETED', 'DEFERRED']).last()
        return active.status if active else None
