from rest_framework import viewsets, filters, decorators
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Donor, DonorDeferral
from .serializers import DonorSerializer, DonorDeferralSerializer

class DonorViewSet(viewsets.ModelViewSet):
    queryset = Donor.objects.all().order_by('-created_at')
    serializer_class = DonorSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['full_name', 'national_id', 'mobile']

    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Exclude donors with active workflows (for New Donors list)
        if self.request.query_params.get('exclude_active') == 'true':
            from clinical.models import DonorWorkflow
            active_statuses = [
                DonorWorkflow.Step.REGISTRATION,
                DonorWorkflow.Step.QUESTIONNAIRE,
                DonorWorkflow.Step.VITALS,
                DonorWorkflow.Step.COLLECTION,
                DonorWorkflow.Step.LABS
            ]
            queryset = queryset.exclude(workflows__status__in=active_statuses)

        # Manual Date Filtering
        date_param = self.request.query_params.get('created_at__date')
        if date_param:
            queryset = queryset.filter(created_at__date=date_param)
            
        return queryset

    @action(detail=True, methods=['get'])
    def history_stats(self, request, pk=None):
        """Returns comprehensive history of a donor for the tracking dashboard."""
        donor = self.get_object()
        from clinical.models import DonorWorkflow
        from inventory.models import BloodComponent

        # Get all workflows except registration
        workflows = donor.workflows.exclude(status=DonorWorkflow.Step.REGISTRATION).order_by('-created_at')
        
        total_donations = workflows.count()
        last_donation = workflows.first()

        history_list = []
        for wf in workflows:
            # Get components for this workflow
            comps = BloodComponent.objects.filter(workflow=wf)
            comp_list = [{
                'id': c.id,
                'type': c.component_type,
                'volume': c.volume_ml,
                'status': c.status
            } for c in comps]

            code = wf.donation_code
            if not code:
                # fallback
                if hasattr(wf, 'blood_draw') and wf.blood_draw and wf.blood_draw.segment_number:
                    code = wf.blood_draw.segment_number
                else:
                    code = f"WF-{wf.id:05d}"

            history_list.append({
                'id': wf.id,
                'date': wf.created_at.isoformat(),
                'code': code,
                'status': wf.status,
                'components': comp_list
            })

        data = {
            'blood_group': donor.blood_group if donor.blood_group else 'Unknown',
            'total_donations': total_donations,
            'last_donation_date': last_donation.created_at.strftime('%Y-%m-%d') if last_donation else 'N/A',
            'timeline': history_list
        }

        return Response(data)

class DonorDeferralViewSet(viewsets.ModelViewSet):
    queryset = DonorDeferral.objects.all().order_by('-created_at')
    serializer_class = DonorDeferralSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['donor__full_name', 'reason']
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
