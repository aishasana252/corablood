from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps

def staff_required(view_func):
    """
    Decorator that ensures the user is either a superuser or has staff access flags.
    Only users with explicit 'Donor' role (and no clinical access) are sent to the donor portal.
    All other authenticated users are allowed if they have is_staff or any can_access flag.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
            
        # Superusers always pass
        if request.user.is_superuser:
            return view_func(request, *args, **kwargs)

        # Staff users always pass (Django admin staff flag)
        if request.user.is_staff:
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
        ])

        # If they have clinical access flags, allow through
        if has_clinical_access:
            return view_func(request, *args, **kwargs)

        # Check if they are explicitly a Donor role — redirect to portal
        is_donor_role = getattr(request.user, 'role', '').lower() == 'donor'
        if is_donor_role:
            return redirect('portal:dashboard')
            
        # No permissions at all — show error and redirect to login
        messages.error(request, "You do not have permission to access the clinical system. Please contact your administrator to assign permissions.")
        return redirect('login')
        
    return _wrapped_view
