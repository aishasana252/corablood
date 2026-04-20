from rest_framework import serializers
from .models import Donor, DonorDeferral

class DonorDeferralSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    
    class Meta:
        model = DonorDeferral
        fields = '__all__'
        read_only_fields = ['created_by', 'created_at']

def _get_active_workflow(obj):
    """Get the newest active (non-completed, non-deferred) workflow for a donor."""
    try:
        # Sort prefetched workflows by created_at descending, then find first active one
        workflows = sorted(obj.workflows.all(), key=lambda wf: wf.created_at, reverse=True)
        return next((wf for wf in workflows if wf.status not in ['COMPLETED', 'DEFERRED']), None)
    except Exception:
        return None

class DonorListSerializer(serializers.ModelSerializer):
    """Ultra-fast serializer for the registry list view with Real-time Status."""
    active_workflow_id = serializers.SerializerMethodField()
    active_workflow_status = serializers.SerializerMethodField()
    
    class Meta:
        model = Donor
        fields = [
            'id', 'national_id', 'full_name', 'gender', 'blood_group', 
            'last_donation_date', 'deferral_status', 'created_at', 
            'active_workflow_id', 'active_workflow_status', 'is_eligible'
        ]

    def get_active_workflow_id(self, obj):
        active = _get_active_workflow(obj)
        return active.id if active else None

    def get_active_workflow_status(self, obj):
        active = _get_active_workflow(obj)
        return active.status if active else None



class DonorSerializer(serializers.ModelSerializer):
    """Full detail serializer (used for single donor view/edit)."""
    deferrals = DonorDeferralSerializer(many=True, read_only=True)
    active_workflow_id = serializers.SerializerMethodField()
    active_workflow_status = serializers.SerializerMethodField()
    
    class Meta:
        model = Donor
        fields = '__all__'

    def get_active_workflow_id(self, obj):
        active = _get_active_workflow(obj)
        return active.id if active else None

    def get_active_workflow_status(self, obj):
        active = _get_active_workflow(obj)
        return active.status if active else None

