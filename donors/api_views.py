from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from clinical.models import DonorWorkflow, Question, Medication, QuestionnaireResponse, DonorMedicationRecord, PostDonationSurvey
from clinical.serializers import WorkflowStatusSerializer, QuestionnaireResponseSerializer
from django.shortcuts import get_object_or_404
from .portal_views_pkg.base import _get_or_create_workflow

class DonorPortalStateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not hasattr(request.user, 'donor_profile'):
            return Response({"success": False, "message": "User is not a donor."}, status=403)
        
        donor = request.user.donor_profile
        workflow = _get_or_create_workflow(request, donor)
        
        if not workflow:
            return Response({
                "success": True,
                "data": {
                    "has_active_workflow": False,
                    "message": "No active donation session."
                }
            })

        # Calculate allowed steps for donor (Questionnaire, Medication, Survey)
        all_steps = [
            {"id": "registration", "name": "Registration", "status": "completed"},
            {"id": "questionnaire", "name": "Questionnaire", "status": "pending"},
            {"id": "medication", "name": "Medication", "status": "pending"},
            {"id": "post_donation", "name": "Support & Survey", "status": "pending"},
        ]
        
        # Mark completions
        current_idx = 0
        status_map = {
            'REGISTRATION': 0,
            'QUESTIONNAIRE': 1,
            'MEDICATION': 2,
            'VITALS': 3, # Clinical step, marks donor part as done
            'COLLECTION': 3,
            'ADVERSE_REACTION': 3,
            'PRE_SEPARATION': 3,
            'COMPONENTS': 3,
            'ATTACHMENT': 3,
            'LABEL': 3,
            'SURVEY': 3,
            'LABS': 3,
            'COMPLETED': 4,
            'POST_DONATION': 3,
        }
        
        current_idx = status_map.get(workflow.status, 1)
        
        for i, step in enumerate(all_steps):
            if i < current_idx:
                step["status"] = "completed"
            elif i == current_idx:
                step["status"] = "current"
            else:
                step["status"] = "locked"

        return Response({
            "success": True,
            "data": {
                "has_active_workflow": True,
                "workflow_id": workflow.id,
                "current_step": workflow.status,
                "steps": all_steps,
                "donor": {
                    "name": donor.full_name,
                    "blood_group": donor.blood_group,
                    "id": donor.id
                }
            }
        })

class DonorPortalQuestionsAPIView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        questions = Question.objects.filter(is_active=True).order_by('order')
        categories = {}
        for q in questions:
            if q.category not in categories:
                categories[q.category] = []
            categories[q.category].append({
                "id": q.id,
                "text": q.text_en,
                "text_ar": q.text_ar,
                "required": q.is_required
            })
        
        return Response({
            "success": True,
            "data": categories
        })

class DonorPortalSubmitAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, step_type):
        if not hasattr(request.user, 'donor_profile'):
            return Response({"success": False}, status=403)
            
        donor = request.user.donor_profile
        workflow = _get_or_create_workflow(request, donor)
        
        if not workflow:
            return Response({"success": False, "message": "No active workflow."}, status=400)

        data = request.data

        if step_type == 'questionnaire':
            QuestionnaireResponse.objects.update_or_create(
                workflow=workflow,
                defaults={
                    'answers': data.get('answers', {}),
                    'signature_data': data.get('signature_data'),
                    'additional_notes': data.get('additional_notes'),
                    'passed': True
                }
            )
            workflow.status = DonorWorkflow.Step.MEDICATION
            workflow.save()
            return Response({"success": True, "next_step": "medication"})

        elif step_type == 'medication':
            record, _ = DonorMedicationRecord.objects.update_or_create(
                workflow=workflow,
                defaults={
                    'is_on_medication': data.get('is_on_medication', False),
                    'notes': data.get('notes', ''),
                    'recorded_by': request.user
                }
            )
            if data.get('medications'):
                record.medications_taken.set(data.get('medications'))
            
            workflow.status = DonorWorkflow.Step.VITALS
            workflow.save()
            return Response({"success": True, "next_step": "vitals"})

        return Response({"success": False, "message": "Invalid step type."}, status=400)

