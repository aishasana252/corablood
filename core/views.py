from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from core.decorators import staff_required
from django.contrib.auth import logout, login as auth_login, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt

@staff_required
def dashboard(request):
    return render(request, 'dashboard.html')

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
