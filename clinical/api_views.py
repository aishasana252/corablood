from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import (
    DonorWorkflow, VitalSigns, QuestionnaireResponse, BloodDraw, 
    DonorMedicationRecord, AdverseReaction, PostDonationSurvey, 
    PreSeparation, PostDonationCare, LabResult, DonationAttachment
)
from .serializers import (
    WorkflowDetailSerializer, VitalSignsSerializer, 
    QuestionnaireResponseSerializer, BloodDrawSerializer,
    DonorMedicationRecordSerializer, AdverseReactionSerializer,
    PostDonationSurveySerializer, PreSeparationSerializer,
    PostDonationCareSerializer, LabResultSerializer,
    DonationAttachmentSerializer
)

# Step Registry: Centralized control for all workflow stages
STEP_REGISTRY = {
    'questionnaire': {
        'serializer': QuestionnaireResponseSerializer,
        'model': QuestionnaireResponse,
        'label': 'Questionnaire'
    },
    'medication': {
        'serializer': DonorMedicationRecordSerializer,
        'model': DonorMedicationRecord,
        'label': 'Medication Review'
    },
    'vitals': {
        'serializer': VitalSignsSerializer,
        'model': VitalSigns,
        'label': 'Vital Signs'
    },
    'collection': {
        'serializer': BloodDrawSerializer,
        'model': BloodDraw,
        'label': 'Blood Draw'
    },
    'post_donation': {
        'serializer': PostDonationCareSerializer,
        'model': PostDonationCare,
        'label': 'Post-Donation Care'
    },
    'adverse_reaction': {
        'serializer': AdverseReactionSerializer,
        'model': AdverseReaction,
        'label': 'Adverse Reaction'
    },
    'survey': {
        'serializer': PostDonationSurveySerializer,
        'model': PostDonationSurvey,
        'label': 'Survey'
    },
    'pre_separation': {
        'serializer': PreSeparationSerializer,
        'model': PreSeparation,
        'label': 'Pre-Separation'
    },
    'labs': {
        'serializer': LabResultSerializer,
        'model': LabResult,
        'label': 'Lab Results'
    },
    'attachment': {
        'serializer': DonationAttachmentSerializer,
        'model': DonationAttachment,
        'label': 'Attachments'
    },
    'label': {
        'serializer': WorkflowDetailSerializer,
        'model': DonorWorkflow,
        'label': 'Unit Labeling'
    },
    'deferred': {
        'serializer': WorkflowDetailSerializer,
        'model': DonorWorkflow,
        'label': 'Deferral'
    }
}



class BaseWorkflowAPIView(APIView):
    def get_workflow(self, donation_id):
        return get_object_or_404(DonorWorkflow, pk=donation_id)

    def success_response(self, data, message="Success"):
        return Response({
            "success": True,
            "data": data,
            "message": message
        })

    def error_response(self, message, errors=None, code=status.HTTP_400_BAD_REQUEST):
        return Response({
            "success": False,
            "message": message,
            "errors": errors
        }, status=code)

class WorkflowStateAPIView(BaseWorkflowAPIView):
    def get(self, request, donation_id):
        workflow = DonorWorkflow.objects.select_related('donor').get(pk=donation_id)
        
        all_steps = workflow.get_workflow_steps()
        current_idx = workflow.get_current_step_index()
        
        tabs = []
        name_map = {
            'REGISTRATION': 'Header',
            'QUESTIONNAIRE': 'Questionnaire',
            'MEDICATION': 'Medication',
            'VITALS': 'Vital Signs',
            'COLLECTION': 'Blood Draw',
            'POST_DONATION': 'Donation Care',
            'ADVERSE_REACTION': 'Adverse Reaction',
            'SURVEY': 'Survey',
            'DEFERRED': 'Deferral',
            'PRE_SEPARATION': 'Pre-Separation',
            'COMPONENTS': 'Components',
            'ATTACHMENT': 'Attachment',
            'LABEL': 'Labeling',
            'LABS': 'Lab Testing',
            'SELF_EXCLUSION': 'Self Exclusion',
            'STATUS_HISTORY': 'Status History',
            'COMPLETED': 'History'
        }

        for i, step_code in enumerate(all_steps):
            tab_status = 'locked'
            if i < current_idx:
                tab_status = 'completed'
            elif i == current_idx:
                tab_status = 'open'

            tabs.append({
                'id': step_code.lower(),
                'name': name_map.get(step_code, step_code.title()),
                'status': tab_status,
                'code': step_code
            })

        return self.success_response({
            'donationId': workflow.id,
            'donationCode': workflow.donation_code or f"WF-{workflow.id:05d}",
            'currentStep': workflow.status.lower(),
            'tabs': tabs,
            'donor': {
                'id': workflow.donor.id,
                'name': workflow.donor.full_name,
                'bloodGroup': workflow.donor.blood_group
            }
        })

class WorkflowStepDetailAPIView(BaseWorkflowAPIView):
    def get(self, request, donation_id, step_slug):
        workflow = self.get_workflow(donation_id)
        
        # Security check: Ensure we aren't looking ahead too far (Optional)
        # if step_slug.upper() != workflow.status and ...
        
        config = STEP_REGISTRY.get(step_slug)
        if not config:
            return self.error_response(f"Step '{step_slug}' not supported in decoupled mode.", code=status.HTTP_404_NOT_FOUND)
            
        # Get data from model
        instance = config['model'].objects.filter(workflow=workflow).first()
        if not instance:
            return self.success_response(None, message="No data for this step yet")
            
        serializer = config['serializer'](instance)
        return self.success_response(serializer.data)

    def post(self, request, donation_id, step_slug):
        workflow = self.get_workflow(donation_id)
        
        # 1. Validation: Is this the current active step?
        if step_slug.upper() != workflow.status:
             return self.error_response(f"Cannot save '{step_slug}'. Current expected step is '{workflow.status}'.")

        config = STEP_REGISTRY.get(step_slug)
        if not config:
            return self.error_response(f"Step '{step_slug}' logic not implemented.")

        # 2. Get or Create Instance
        instance = config['model'].objects.filter(workflow=workflow).first()
        serializer = config['serializer'](instance, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save(workflow=workflow)
            
            # 3. Transition Control: Move to next step automatically
            all_steps = workflow.get_workflow_steps()
            current_idx = workflow.get_current_step_index()
            
            if current_idx < len(all_steps) - 1:
                workflow.status = all_steps[current_idx + 1]
                workflow.save()

            return self.success_response({
                "saved_data": serializer.data,
                "next_step": workflow.status.lower()
            }, message=f"{config['label']} saved successfully.")
            
        return self.error_response("Validation failed", errors=serializer.errors)
