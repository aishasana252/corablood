# portal_views package - Re-exports all views to maintain backward compatibility
# This file ensures that existing imports like `from . import portal_views` continue to work
# while the logic is now properly organized in sub-modules.

from .auth import portal_register, portal_login, portal_logout
from .dashboard import portal_dashboard
from .profile import portal_profile
from .workflow import portal_questionnaire, portal_medication, portal_post_donation

__all__ = [
    'portal_register',
    'portal_login',
    'portal_logout',
    'portal_dashboard',
    'portal_profile',
    'portal_questionnaire',
    'portal_medication',
    'portal_post_donation',
]
