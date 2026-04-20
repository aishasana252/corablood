from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from core.decorators import staff_required
from django.contrib import messages
from django.http import JsonResponse
from .models import Donor, Nationality, DonorAppointment

@staff_required
def appointments_list(request):
    """Admin view to see and manage all donor appointments."""

    status_filter = request.GET.get('status', '')
    qs = DonorAppointment.objects.select_related('donor').order_by('-appointment_date', '-appointment_time')
    if status_filter:
        qs = qs.filter(status=status_filter)

    return render(request, 'donors/appointments_list.html', {
        'appointments': qs,
        'status_filter': status_filter,
        'statuses': DonorAppointment.STATUS_CHOICES,
    })

@staff_required
def appointment_action(request, pk):
    """Admin can accept/cancel an appointment and sync workflow."""

    appt = get_object_or_404(DonorAppointment, pk=pk)
    action = request.POST.get('action')

    if action == 'accept':
        appt.status = 'CONFIRMED'
        appt.save()
        
        # Sychronize Workflow on Confirmation
        from clinical.services import WorkflowService
        workflow = WorkflowService.get_active_workflow(appt.donor)
        
        if workflow:
            # Link to this specific appointment
            workflow.appointment = appt
            
            from clinical.models import DonorWorkflow
            workflow.workflow_type = DonorWorkflow.WorkflowType.WHOLE_BLOOD
            
            # Use Appointment ID as the base for Donation Code
            if not workflow.donation_code:
                workflow.donation_code = f"CB-{appt.id:04d}"
                
            workflow.save()
            
        messages.success(request, f"Appointment for {appt.donor.full_name} confirmed & Workflow Synced.")
    elif action == 'cancel':
        appt.status = 'CANCELLED'
        appt.save()
        messages.warning(request, f"Appointment for {appt.donor.full_name} cancelled.")

    return redirect('appointments_list')

from clinical.models import DonorWorkflow

@staff_required
def appointment_workflow(request, pk):
    """Start or resume a workflow for a specific confirmed appointment."""
        
    appt = get_object_or_404(DonorAppointment, pk=pk)
    
    if appt.status != 'CONFIRMED':
        messages.warning(request, "Cannot start workflow for unconfirmed appointments.")
        return redirect('appointments_list')
        
    # Check if a workflow already exists for this appointment
    if hasattr(appt, 'workflow') and appt.workflow is not None:
        active_workflow = appt.workflow
    else:
        # Default to WHOLE_BLOOD for all workflows
        workflow_type = DonorWorkflow.WorkflowType.WHOLE_BLOOD
            
        active_workflow = DonorWorkflow.objects.create(
            donor=appt.donor,
            appointment=appt,
            workflow_type=workflow_type,
            status=DonorWorkflow.Step.QUESTIONNAIRE,
            created_by=request.user
        )

    print(f"DEBUG: Appointment {appt.id} Workflow Context: {active_workflow} with type {active_workflow.workflow_type}")
    return render(request, 'donors/workflow.html', {
        'donor': appt.donor,
        'active_workflow': active_workflow,
        'is_eligible': appt.donor.is_eligible,
        'next_eligible_date': appt.donor.next_eligible_date
    })



@staff_required
def settings_nationality(request):
    if request.method == 'POST':
        item_id = request.POST.get('item_id')
        name_en = request.POST.get('name_en')
        name_ar = request.POST.get('name_ar')
        is_active = request.POST.get('is_active') == 'on'
        is_default = request.POST.get('is_default') == 'on'
        
        if is_default:
            # Unset other defaults
            Nationality.objects.update(is_default=False)
            
        if item_id:
            # Edit
            n = get_object_or_404(Nationality, pk=item_id)
            n.name_en = name_en
            n.name_ar = name_ar
            n.is_active = is_active
            n.is_default = is_default
            n.save()
            messages.success(request, "Nationality updated successfully.")
        else:
            # Create
            Nationality.objects.create(
                name_en=name_en,
                name_ar=name_ar,
                is_active=is_active,
                is_default=is_default
            )
            messages.success(request, "Nationality added successfully.")
            
        return redirect('settings_nationality')
        
    nationalities = Nationality.objects.all()
    return render(request, 'donors/settings_nationality.html', {'nationalities': nationalities})
import datetime

@staff_required
def donor_list(request):
    donors = Donor.objects.all().order_by('-created_at')[:50]
    return render(request, 'donors/list.html', {'donors': donors})

@staff_required
def recent_donors(request):
    # Just render the template, the JS will fetch key data via API
    return render(request, 'donors/recent_list.html')

@staff_required
def donor_add(request):
    if request.method == 'POST':
        try:
            donor = Donor.objects.create(
                national_id=request.POST.get('national_id'),
                full_name=request.POST.get('full_name').upper(),
                date_of_birth=request.POST.get('date_of_birth'),
                gender=request.POST.get('gender'),
                nationality=request.POST.get('nationality'),
                mobile=request.POST.get('mobile'),
                blood_group=request.POST.get('blood_group', 'UNKNOWN'),
                created_by=request.user
            )
            messages.success(request, f"Donor {donor.full_name} registered successfully.")
            return redirect('donor_workflow', pk=donor.pk)
        except Exception as e:
             return render(request, 'donors/add.html', {'error': str(e)})
             
    nationalities = Nationality.objects.filter(is_active=True).order_by('-is_default', 'name_en')
    return render(request, 'donors/add.html', {'nationalities': nationalities})

@staff_required
def deferred_donors(request):
    donors = Donor.objects.filter(workflows__status='DEFERRED').distinct()
    return render(request, 'donors/deferred_list.html', {'donors': donors})

@staff_required
def not_completed_donors(request):
    # Active workflows (Not COMPLETED and Not DEFERRED)
    from clinical.models import DonorWorkflow
    workflows = DonorWorkflow.objects.exclude(
        status__in=[DonorWorkflow.Step.COMPLETED, DonorWorkflow.Step.DEFERRED]
    ).order_by('-created_at')
    
    return render(request, 'donors/incomplete_list.html', {'workflows': workflows})

from clinical.services import WorkflowService

@staff_required
def donor_workflow(request, pk):
    donor = get_object_or_404(Donor, pk=pk)
    active_workflow = WorkflowService.get_active_workflow(donor)
    if not active_workflow:
        # Fallback: Get the most recent workflow to show history/status
        active_workflow = donor.workflows.order_by('-created_at').first()

    print(f"DEBUG: Donor {donor.id} Workflow Context: {active_workflow}")
    return render(request, 'donors/workflow.html', {
        'donor': donor,
        'active_workflow': active_workflow,
        'is_eligible': donor.is_eligible,
        'next_eligible_date': donor.next_eligible_date
    })

@staff_required
def donor_edit(request, pk):
    donor = get_object_or_404(Donor, pk=pk)
    
    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        mobile = request.POST.get('mobile')
        dob = request.POST.get('dob')
        email = request.POST.get('email')
        blood_type = request.POST.get('blood_type')
        status = request.POST.get('status')
        
        try:
            donor.full_name = full_name
            donor.mobile = mobile
            if dob: donor.dob = dob
            if email: donor.email = email
            if blood_type: donor.blood_group = blood_type
            if status: donor.status = status
            donor.save()
            
            # Sync user if needed
            if donor.user:
                if email: donor.user.email = email
                donor.user.save()
                
            messages.success(request, f"Donor {donor.full_name} updated successfully.")
            return redirect('donor_list')
        except Exception as e:
            messages.error(request, f"Error updating donor: {str(e)}")
            
    return render(request, 'donors/donor_edit.html', {'donor': donor})
