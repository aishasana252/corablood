from rest_framework import permissions

class IsStaffOrClinicalAdmin(permissions.BasePermission):
    """
    Custom permission to only allow superusers or users with specific clinical access flags.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
            
        if request.user.is_superuser:
            return True

        # Check for ANY clinical access flag
        return any([
            request.user.can_access_donors,
            request.user.can_access_donations,
            request.user.can_access_settings,
            request.user.can_access_inventory,
            request.user.can_access_reports,
            request.user.can_access_clinical,
            request.user.can_access_orders,
            request.user.can_access_dashboard
        ])
