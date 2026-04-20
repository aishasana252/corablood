from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps

def staff_required(view_func):
    """
    Decorator that ensures the user is either a superuser or has staff access flags.
    If the user is a Donor without specific staff permissions, they are redirected to their portal.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
            
        if request.user.is_superuser:
            return view_func(request, *args, **kwargs)

        # Check if they have ANY clinical permission flag
        has_clinical_access = any([
            request.user.can_access_donors,
            request.user.can_access_donations,
            request.user.can_access_settings,
            request.user.can_access_inventory,
            request.user.can_access_reports,
            request.user.can_access_clinical,
            request.user.can_access_orders,
            request.user.can_access_dashboard,
            request.user.is_staff
        ])

        # Check if they are explicitly a donor
        is_donor = getattr(request.user, 'role', '').lower() == 'donor'
        is_staff_or_admin = request.user.is_staff or request.user.is_superuser
        
        # If they are a Donor role AND not explicitly staff, they go to donor portal
        if is_donor and not is_staff_or_admin:
            return redirect('portal:dashboard')
            
        if not has_clinical_access and not is_staff_or_admin:
            # Missing both flags and staff status
            messages.error(request, "You do not have permission to access the clinical system.")
            return redirect('logout')

        return view_func(request, *args, **kwargs)
        
    return _wrapped_view
