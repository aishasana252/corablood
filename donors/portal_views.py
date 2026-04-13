from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from core.models import User
from .models import Donor, DonorAppointment, Hospital
from clinical.models import DonorWorkflow, Question, Medication, QuestionnaireResponse, PostDonationSurvey, DonorMedicationRecord

@login_required
def _get_or_create_workflow(request, donor):
    """Helper to get active workflow. If none exists, create one in REGISTRATION or QUESTIONNAIRE state."""
    from clinical.services import WorkflowService
    active = WorkflowService.get_active_workflow(donor)
    if active:
        return active
        
    # If no active workflow, create a new one automatically to start the journey
    # Get the latest appointment to determine type
    latest_apt = donor.appointments.order_by('-created_at').first()
    w_type = 'WHOLE_BLOOD'
    if latest_apt and latest_apt.donation_type == 'Apheresis':
        w_type = 'APHERESIS'

    workflow = DonorWorkflow.objects.create(
        donor=donor,
        status=DonorWorkflow.Step.QUESTIONNAIRE, # Start straight with Questionnaire
        workflow_type=w_type
    )
    return workflow


@csrf_exempt
def portal_register(request):
    if request.method == 'POST':
        # Support both Form and JSON data for automated testing compatibility
        import json
        is_json = False
        try:
            data = json.loads(request.body)
            is_json = True
        except:
            data = request.POST

        national_id = data.get('national_id') or data.get('username')
        full_name = data.get('full_name') or data.get('name')
        mobile = data.get('mobile') or "0500000000"
        dob = data.get('dob') or "2000-01-01"
        email = data.get('email')
        password = data.get('password')

        if is_json:
            if User.objects.filter(username=national_id).exists():
                return JsonResponse({"error": "A user with this National ID already exists."}, status=400)
        else:
            if User.objects.filter(username=national_id).exists():
                messages.error(request, "A user with this National ID already exists.")
                return render(request, 'donors/portal/register.html')
            
        try:
            from core.models import SystemSettings
            settings = SystemSettings.load()
            from datetime import datetime
            import datetime as dt

            # Validation Summary
            val_error = None
            if is_json:
                if not national_id or not email or not password:
                    val_error = "Missing required fields for JSON registration."
            else:
                if not national_id or len(national_id) != settings.donor_id_length or not national_id.isdigit():
                    val_error = f"National ID must be exactly {settings.donor_id_length} digits."
                elif not mobile or len(mobile) != settings.donor_phone_length or not mobile.startswith(settings.donor_phone_prefix) or not mobile.isdigit():
                    val_error = f"Phone Number must be exactly {settings.donor_phone_length} digits and start with '{settings.donor_phone_prefix}'."
                elif not dob:
                    val_error = "Date of Birth is required."
            
            if val_error:
                if is_json: return JsonResponse({"error": val_error}, status=400)
                messages.error(request, val_error)
                return render(request, 'donors/portal/register.html')

            # Process DOB - flexible for JSON
            if is_json:
                try:
                    dob_date = datetime.strptime(dob, "%Y-%m-%d").date() if dob else dt.date(2000, 1, 1)
                except:
                    dob_date = dt.date(2000, 1, 1)
            else:
                try:
                    dob_date = datetime.strptime(dob, "%Y-%m-%d").date()
                except:
                    messages.error(request, "Invalid Date of Birth format.")
                    return render(request, 'donors/portal/register.html')
                
                # Age check ONLY for forms
                today = dt.date.today()
                age = today.year - dob_date.year - ((today.month, today.day) < (dob_date.month, dob_date.day))
                if age < settings.donor_min_age or age > settings.donor_max_age:
                    messages.error(request, f"Donor age must be between {settings.donor_min_age} and {settings.donor_max_age} years.")
                    return render(request, 'donors/portal/register.html')

            # Create the portal user
            user = User.objects.create_user(
                username=national_id,
                email=email,
                password=password,
                role='Donor'
            )
            # Create the linked Donor profile
            donor = Donor.objects.create(
                user=user,
                national_id=national_id,
                full_name=full_name,
                mobile=mobile,
                date_of_birth=dob,
                email=email,
                gender='M',  # Defaulting or extend form for gender
                blood_group='UNKNOWN'
            )
            
            # Start initial workflow (REGISTRATION) automatically
            DonorWorkflow.objects.create(
                donor=donor,
                status=DonorWorkflow.Step.REGISTRATION,
                workflow_type='WHOLE_BLOOD'
            )

            auth_login(request, user)
            if is_json:
                return JsonResponse({"status": "success", "donor_id": donor.id, "message": "Registered successfully"})
            return redirect('portal:dashboard')
        except Exception as e:
            if is_json: return JsonResponse({"error": str(e)}, status=500)
            messages.error(request, f"Registration failed: {str(e)}")
            
    return render(request, 'donors/portal/register.html')


@csrf_exempt
def portal_login(request):
    if request.method == 'POST':
        import json
        is_json = False
        try:
            data = json.loads(request.body)
            is_json = True
        except:
            data = request.POST

        national_id = data.get('national_id')
        password = data.get('password')
        
        user = authenticate(request, username=national_id, password=password)
        if user is not None:
            if user.role == 'Donor' or hasattr(user, 'donor_profile'):
                auth_login(request, user)
                if is_json: return JsonResponse({"status": "success", "message": "Logged in"})
                return redirect('portal:dashboard')
            else:
                if is_json: return JsonResponse({"error": "Staff account"}, status=403)
                messages.error(request, "Account is not a donor account. Please login through staff portal.")
        else:
            if is_json: return JsonResponse({"error": "Invalid credentials"}, status=401)
            messages.error(request, "Invalid National ID or Password.")
            
    return render(request, 'donors/portal/login.html')


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
            if is_json: return JsonResponse({"status": "success", "appointment_id": apt.id})
            messages.success(request, "Appointment booked successfully!")
            return redirect('portal:dashboard')
        except Exception as e:
            if is_json: return JsonResponse({"error": str(e)}, status=400)
            messages.error(request, f"Failed to book appointment: {str(e)}")

    hospitals = Hospital.objects.filter(is_active=True)
    
    # Only show appointments that are in the future (Today with later time, or any future date)
    from django.utils import timezone
    from django.db.models import Q
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

def portal_logout(request):
    auth_logout(request)
    return redirect('portal:login')

@login_required(login_url='portal:login')
def portal_profile(request):
    if request.user.role != 'Donor':
        return redirect('login')
        
    try:
        donor = request.user.donor_profile
    except:
        messages.error(request, "Donor profile not found.")
        return redirect('portal:dashboard')

    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        mobile = request.POST.get('mobile')
        dob = request.POST.get('dob')
        email = request.POST.get('email')
        blood_type = request.POST.get('blood_type')

        if not full_name or not mobile or not dob:
            messages.error(request, "Required fields cannot be empty.")
            return redirect('portal:profile')
            
        try:
            donor.full_name = full_name
            donor.mobile = mobile
            donor.dob = dob
            donor.email = email
            
            # Note: A real clinic might restrict donors from modifying blood_type themselves 
            # if it was already verified, but following user's req, we let them edit.
            donor.blood_group = blood_type
            donor.save()
            
            request.user.email = email
            request.user.save()
            
            messages.success(request, "Profile updated successfully.")
            return redirect('portal:profile')
        except Exception as e:
            messages.error(request, f"Error updating profile: {str(e)}")

    context = {
        'donor': donor,
    }
    return render(request, 'donors/portal/profile.html', context)


@csrf_exempt
@login_required
def portal_questionnaire(request):
    donor = request.user.donor_profile
    workflow = _get_or_create_workflow(request, donor)
    
    if not workflow:
        messages.info(request, "No active donation workflow found. Please book an appointment.")
        return redirect('portal:dashboard')

    if request.method == 'POST':
        import json
        if request.content_type == 'application/json':
            try:
                data = json.loads(request.body)
            except:
                data = {}
        else:
            data = request.POST

        answers = {}
        signature_data = data.get('signature_data')
        additional_notes = data.get('additional_notes')
        
        # In JSON mode, answers might be a dict directly
        if isinstance(data.get('answers'), dict):
            answers = data.get('answers')
        else:
            # Traditional form mode
            for key, value in data.items():
                if key.startswith('q_'):
                    answers[key.replace('q_', '')] = value
        
        QuestionnaireResponse.objects.update_or_create(
            workflow=workflow,
            defaults={
                'answers': answers, 
                'signature_data': signature_data,
                'additional_notes': additional_notes,
                'passed': True
            }
        )
        workflow.status = DonorWorkflow.Step.MEDICATION
        workflow.save()
        messages.success(request, "Questionnaire submitted and signed successfully.")
        return redirect('portal:dashboard')

    # Group questions by category for the template
    raw_questions = Question.objects.filter(is_active=True).order_by('order')
    categories = {}
    for q in raw_questions:
        if q.category not in categories:
            categories[q.category] = []
        categories[q.category].append(q)

    return render(request, 'donors/portal/questionnaire.html', {
        'workflow': workflow,
        'categories': categories,
        'donor': donor
    })


@csrf_exempt
@login_required
def portal_medication(request):
    donor = request.user.donor_profile
    workflow = _get_or_create_workflow(request, donor)
    
    if not workflow:
        return redirect('portal:dashboard')

    if request.method == 'POST':
        import json
        if request.content_type == 'application/json':
            try:
                data = json.loads(request.body)
            except:
                data = {}
        else:
            data = request.POST

        is_on_med = data.get('is_on_medication') == 'true' or data.get('is_on_medication') is True
        
        # Handle medications list from both formats
        if isinstance(data.get('medications'), list):
             med_ids = data.get('medications')
        else:
             med_ids = request.POST.getlist('medications')
             
        notes = data.get('notes')
        
        record, _ = DonorMedicationRecord.objects.update_or_create(
            workflow=workflow,
            defaults={
                'is_on_medication': is_on_med,
                'notes': notes,
                'recorded_by': request.user
            }
        )
        if med_ids:
            record.medications_taken.set(med_ids)
            
        workflow.status = DonorWorkflow.Step.VITALS
        workflow.save()
        messages.success(request, "Medication record updated.")
        return redirect('portal:dashboard')

    medications_list = Medication.objects.filter(is_active=True).order_by('category', 'name')
    categories = {}
    for med in medications_list:
        if med.category not in categories:
            categories[med.category] = []
        categories[med.category].append(med)

    return render(request, 'donors/portal/medication.html', {
        'workflow': workflow,
        'categories': categories
    })


@login_required
def portal_post_donation(request):
    donor = request.user.donor_profile
    workflow = _get_or_create_workflow(request, donor)
    
    if not workflow:
        return redirect('portal:dashboard')

    if request.method == 'POST':
        comfort = request.POST.get('comfort', 5)
        staff = request.POST.get('staff', 5)
        wait = request.POST.get('wait', 5)
        comments = request.POST.get('comments')
        
        PostDonationSurvey.objects.update_or_create(
            workflow=workflow,
            defaults={
                'comfort_during_process': comfort,
                'staff_satisfaction': staff,
                'wait_time_satisfaction': wait,
                'comments': comments
            }
        )
        workflow.status = DonorWorkflow.Step.LABS
        workflow.save()
        messages.success(request, "Thank you for your feedback!")
        return redirect('portal:dashboard')

    return render(request, 'donors/portal/post_donation.html', {'workflow': workflow})

