from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q
from donors.models import Donor, DonorAppointment, Hospital
from clinical.models import DonorWorkflow
from .base import _get_or_create_workflow


@login_required
def portal_dashboard(request):
    try:
        donor = request.user.donor_profile
    except Donor.DoesNotExist:
        messages.error(request, "No donor profile found for this account.")
        return redirect('logout')

    if request.method == 'POST':
        ct = request.content_type or request.META.get('CONTENT_TYPE', '')
        is_json = 'application/json' in ct
        if is_json:
            import json
            try:
                data = json.loads(request.body)
            except:
                data = {}
        else:
            data = request.POST

        hospital_id = data.get('hospital_id')
        date = data.get('appointment_date')
        time = data.get('appointment_time')
        donation_type = data.get('donation_type')
        blood_type = data.get('blood_type')

        try:
            hospital_obj = Hospital.objects.get(id=hospital_id)
            apt = DonorAppointment.objects.create(
                donor=donor,
                hospital=hospital_obj,
                appointment_date=date,
                appointment_time=time,
                donation_type=donation_type,
                blood_group=blood_type
            )
            if is_json:
                return JsonResponse({"status": "success", "appointment_id": apt.id})
            messages.success(request, "Appointment booked successfully!")
            return redirect('portal:dashboard')
        except Exception as e:
            if is_json:
                return JsonResponse({"error": str(e)}, status=400)
            messages.error(request, f"Failed to book appointment: {str(e)}")

    hospitals = Hospital.objects.filter(is_active=True)
    now = timezone.now()

    appointments = donor.appointments.select_related('hospital').filter(
        Q(appointment_date__gt=now.date()) |
        Q(appointment_date=now.date(), appointment_time__gte=now.time())
    ).exclude(status__in=['COMPLETED', 'CANCELLED']).order_by('appointment_date', 'appointment_time')

    active_workflow = _get_or_create_workflow(request, donor)
    past_donations = DonorWorkflow.objects.filter(donor=donor).exclude(id=active_workflow.id).order_by('-created_at')

    return render(request, 'donors/portal/dashboard.html', {
        'donor': donor,
        'appointments': appointments,
        'active_workflow': active_workflow,
        'hospitals': hospitals,
        'past_donations': past_donations
    })
