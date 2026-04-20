from django.shortcuts import render, redirect, get_object_or_404
from donors.models import Donor
from clinical.models import DonorWorkflow

def _get_or_create_workflow(request, donor):
    """Helper to get active workflow. If none exists, create one in REGISTRATION or QUESTIONNAIRE state."""
    from clinical.services import WorkflowService
    active = WorkflowService.get_active_workflow(donor)
    if active:
        return active
        
    # If no active workflow, create a new one automatically to start the journey
    latest_apt = donor.appointments.order_by('-created_at').first()
    w_type = 'WHOLE_BLOOD'
    if latest_apt and latest_apt.donation_type == 'APHERESIS':
        w_type = 'APHERESIS'

    workflow = DonorWorkflow.objects.create(
        donor=donor,
        status=DonorWorkflow.Step.QUESTIONNAIRE, 
        workflow_type=w_type
    )
    return workflow
