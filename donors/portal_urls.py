from django.urls import path
from . import portal_views

app_name = 'portal'

urlpatterns = [
    path('register/', portal_views.portal_register, name='register'),
    path('login/', portal_views.portal_login, name='login'),
    path('dashboard/', portal_views.portal_dashboard, name='dashboard'),
    path('profile/', portal_views.portal_profile, name='profile'),
    path('logout/', portal_views.portal_logout, name='logout'),
    
    # Workflow Steps
    path('workflow/questionnaire/', portal_views.portal_questionnaire, name='questionnaire'),
    path('workflow/medication/', portal_views.portal_medication, name='medication'),
    path('workflow/post-donation/', portal_views.portal_post_donation, name='post_donation'),
]
