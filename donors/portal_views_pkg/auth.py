from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from core.models import User
from donors.models import Donor
from clinical.models import DonorWorkflow

@csrf_exempt
def portal_register(request):
    if request.method == 'POST':
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
                
                today = dt.date.today()
                age = today.year - dob_date.year - ((today.month, today.day) < (dob_date.month, dob_date.day))
                if age < settings.donor_min_age or age > settings.donor_max_age:
                    messages.error(request, f"Donor age must be between {settings.donor_min_age} and {settings.donor_max_age} years.")
                    return render(request, 'donors/portal/register.html')

            user = User.objects.create_user(
                username=national_id,
                email=email,
                password=password,
                role='Donor'
            )
            donor = Donor.objects.create(
                user=user,
                national_id=national_id,
                full_name=full_name,
                mobile=mobile,
                date_of_birth=dob,
                email=email,
                gender='M',
                blood_group='UNKNOWN'
            )
            
            DonorWorkflow.objects.create(
                donor=donor,
                status=DonorWorkflow.Step.QUESTIONNAIRE,
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
                messages.error(request, "Account is not a donor account.")
        else:
            if is_json: return JsonResponse({"error": "Invalid credentials"}, status=401)
            messages.error(request, "Invalid National ID or Password.")
            
    return render(request, 'donors/portal/login.html')

def portal_logout(request):
    auth_logout(request)
    return redirect('portal:login')
