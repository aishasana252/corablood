from rest_framework import viewsets, filters, decorators
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db.models import Prefetch
from .models import Donor, DonorDeferral
from .serializers import DonorSerializer, DonorDeferralSerializer, DonorListSerializer
from clinical.models import DonorWorkflow # Import at top

class DonorViewSet(viewsets.ModelViewSet):
    queryset = Donor.objects.all().prefetch_related(
        Prefetch('workflows', queryset=DonorWorkflow.objects.order_by('-created_at'))
    ).order_by('-created_at')
    
    def get_serializer_class(self):
        if self.action == 'list':
            return DonorListSerializer
        return DonorSerializer

    def get_queryset(self):
        # Bare minimum queryset for debugging speed issues
        return super().get_queryset()


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
                'volume': c.volume,
                'status': c.status
            } for c in comps]

            code = wf.donation_code
            if not code:
                # fallback
                if hasattr(wf, 'blood_draw') and wf.blood_draw and wf.blood_draw.segment_number:
                    code = wf.blood_draw.segment_number
                else:
                    code = f"WF-{wf.id:05d}"

            # Get vitals
            vitals = getattr(wf, 'vitals', None)
            draw = getattr(wf, 'blood_draw', None)

            f_vol = comps.filter(component_type__icontains='RCC').first().volume if comps.filter(component_type__icontains='RCC').exists() else ''
            s_vol = comps.filter(component_type__icontains='FFP').first().volume if comps.filter(component_type__icontains='FFP').exists() else ''
            t_vol = comps.filter(component_type__icontains='Platelet').first().volume if comps.filter(component_type__icontains='Platelet').exists() else ''
            bp = ''
            if vitals and vitals.bp_systolic and vitals.bp_diastolic:
                bp = f"{vitals.bp_systolic}/{vitals.bp_diastolic}"
            
            history_list.append({
                'id': wf.id,
                'date': wf.created_at.isoformat(),
                'code': code,
                'status': wf.status,
                'components': comp_list,
                'vitals': {
                    'height': getattr(vitals, 'height', ''),
                    'weight': vitals.weight_kg if vitals else '',
                    'hgb': vitals.hemoglobin if vitals else '',
                    'pulse': vitals.pulse if vitals else '',
                    'bp': bp,
                    'temp': vitals.temperature_c if vitals else ''
                },
                'draw': {
                    'arm': draw.arm if draw else '',
                    'blood_nature': 'Whole Blood', # Default for generic tracking
                    'patient_name': '', # Typically not known here until crossmatched
                    'f_vol': f_vol,
                    's_vol': s_vol,
                    't_vol': t_vol,
                },
                'donor_name': donor.full_name,
                'blood_group': donor.blood_group,
                'by': wf.created_by.get_full_name() if wf.created_by else 'System'
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
