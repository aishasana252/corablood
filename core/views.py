from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from core.decorators import staff_required
from django.contrib.auth import logout, login as auth_login, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt

from donors.models import Donor
from clinical.models import DonorWorkflow
from inventory.models import BloodComponent
from orders.models import BloodOrder, Crossmatch
from django.db.models import Count, Q

@staff_required
def dashboard(request):
    # Core Stats
    total_donors = Donor.objects.count()
    total_units = BloodComponent.objects.filter(status='AVAILABLE').count()
    total_requests = BloodOrder.objects.exclude(status='CANCELLED').count()
    pending_requests = BloodOrder.objects.filter(status='PENDING').count()
    
    # Recent Activities Aggregation
    activities = []
    
    # 1. Completed Donations
    completed_donations = DonorWorkflow.objects.filter(status='COMPLETED').select_related('donor').order_by('-updated_at')[:5]
    for d in completed_donations:
        activities.append({
            'type': 'donation',
            'title': 'Donation Completed',
            'description': f"Donor {d.donor.national_id} • {d.get_workflow_type_display()}",
            'time': d.updated_at,
            'icon': 'success'
        })
        
    # 2. Issued Units
    issued_orders = BloodOrder.objects.filter(status='ISSUED').order_by('-updated_at')[:5]
    for o in issued_orders:
        activities.append({
            'type': 'issue',
            'title': 'Unit Issued',
            'description': f"Unit for {o.patient_full_name} ({o.urgency})",
            'time': o.updated_at,
            'icon': 'info'
        })
        
    # 3. Incompatible Crossmatches
    failed_crossmatches = Crossmatch.objects.filter(is_compatible=False).select_related('order', 'unit').order_by('-tested_at')[:5]
    for c in failed_crossmatches:
        activities.append({
            'type': 'crossmatch',
            'title': 'Crossmatch Incompatible',
            'description': f"Unit #{c.unit.unit_number} • Patient {c.order.patient_mrn}",
            'time': c.tested_at,
            'icon': 'warning'
        })
        
    # Sort all by time
    activities.sort(key=lambda x: x['time'], reverse=True)
    recent_activities = activities[:8] # Show top 8
    
    context = {
        'total_donors': total_donors,
        'total_units': total_units,
        'total_requests': total_requests,
        'pending_requests': pending_requests,
        'recent_activities': recent_activities,
    }
    return render(request, 'dashboard.html', context)

def staff_login(request):
    """Custom login for staff that rejects Donor-only accounts."""
    if request.user.is_authenticated:
        return redirect('dashboard')
        
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            
            # Reject Donors who don't have clinical permissions
            is_donor = (user.role.lower() == 'donor' or hasattr(user, 'donor_profile'))
            has_access = any([
                user.can_access_dashboard,
                user.can_access_donors,
                user.is_staff,
                user.is_superuser
            ])
            
            if is_donor and not has_access:
                messages.error(request, "This account is a Donor account. Please use the Donor Portal to login.")
                return render(request, 'login.html', {'form': form})
            
            auth_login(request, user)
            return redirect('dashboard')
    else:
        form = AuthenticationForm()
        
    return render(request, 'login.html', {'form': form})

@csrf_exempt
def custom_logout(request):
    logout(request)
    return redirect('login')
