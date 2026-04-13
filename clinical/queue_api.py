from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import DonorWorkflow

class WorkflowQueueViewSet(viewsets.ViewSet):
    """
    API ViewSet for managing the various workflow queues.
    Endpoints:
    GET /api/workflow/queue/?step=QUESTIONNAIRE
    GET /api/workflow/queue/?donation_id=123
    """
    
    def list(self, request):
        step = request.query_params.get('step')
        donation_id = request.query_params.get('donation_id')
        
        queryset = DonorWorkflow.objects.all().select_related('donor')
        
        # Filter by Step
        if step:
            # Map frontend step names to DB values if needed, or rely on exact match
            # DB Values: REGISTRATION, QUESTIONNAIRE, VITALS, COLLECTION, LABS
            queryset = queryset.filter(status=step)
            
        # Filter by ID (Focused View)
        if donation_id:
            queryset = queryset.filter(pk=donation_id)
            
        # Filter by status exclusion (for Active Tab)
        status_exclude = request.query_params.get('status__exclude')
        if status_exclude:
            exclusions = status_exclude.split(',')
            queryset = queryset.exclude(status__in=exclusions)
            
        # Default sort
        queryset = queryset.order_by('-created_at') # Newest first
        print(f"DEBUG QUEUE API: Step={step} Exclude={status_exclude} Count={queryset.count()}")
        
        data = []
        for wf in queryset:
            data.append({
                'id': wf.id,
                'donation_code': wf.donation_code if wf.donation_code else f"DIN-{wf.id:06d}",
                'status': wf.status,
                'created_at': wf.created_at,
                'donor_id': wf.donor.id, # Flat ID for URL
                'donor_name': wf.donor.full_name, # Flat name
                'donor_id_number': wf.donor.national_id, # Flat ID number
                'donor_details': {
                    'full_name': wf.donor.full_name,
                    'national_id': wf.donor.national_id,
                    'blood_group': wf.donor.blood_group,
                    'iqama_id': wf.donor.national_id
                },
                'site': 'Main Center',
                'blood_nature': wf.blood_draw.blood_nature if hasattr(wf, 'blood_draw') else 'Unknown',
                'donation_date': wf.created_at.isoformat()
            })
            
        return Response(data)

    @action(detail=False, methods=['get'])
    def counts(self, request):
        """
        Return counts for all steps to show badges in navigation
        """
        counts = {
            'REGISTRATION': DonorWorkflow.objects.filter(status='REGISTRATION').count(),
            'QUESTIONNAIRE': DonorWorkflow.objects.filter(status='QUESTIONNAIRE').count(),
            'VITALS': DonorWorkflow.objects.filter(status='VITALS').count(),
            'COLLECTION': DonorWorkflow.objects.filter(status='COLLECTION').count(),
            'LABS': DonorWorkflow.objects.filter(status='LABS').count(),
        }
        return Response(counts)
