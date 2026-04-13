from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .viewsets import DonorViewSet, DonorDeferralViewSet

router = DefaultRouter()
router.register(r'api/donors', DonorViewSet)
router.register(r'api/deferrals', DonorDeferralViewSet)

urlpatterns = [
    path('', views.donor_list, name='donor_list'),
    path('recent/', views.recent_donors, name='recent_donors'),
    path('add/', views.donor_add, name='donor_add'),
    path('<int:pk>/edit/', views.donor_edit, name='donor_edit'),
    path('deferred/', views.deferred_donors, name='deferred_donors'),
    path('incomplete/', views.not_completed_donors, name='not_completed_donors'),
    path('settings/nationality/', views.settings_nationality, name='settings_nationality'),
    path('<int:pk>/workflow/', views.donor_workflow, name='donor_workflow'),

    # Appointments (Admin)
    path('appointments/', views.appointments_list, name='appointments_list'),
    path('appointments/<int:pk>/action/', views.appointment_action, name='appointment_action'),
    
    # API
    path('', include(router.urls)),
]
