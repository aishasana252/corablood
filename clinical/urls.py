from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .views import component_print_label, complete_labeling

router = DefaultRouter()
router.register(r'api/donations', views.DonationWorkflowViewSet, basename='donation-api')
router.register(r'api/workflow/queue', views.WorkflowQueueViewSet, basename='workflow-queue') # New Queue API
router.register(r'api/questions', views.QuestionViewSet, basename='questions')
router.register(r'api/vital-limits', views.VitalLimitViewSet, basename='vital-limits')

urlpatterns = [
    path('reports/cc-pending-view/', views.component_culture_pending, name='cc_pending_view'), # Unique Path
    path('start/<int:donor_id>/', views.start_donation, name='start_donation'),
    path('', include(router.urls)), # Expose API endpoints
    
    path('workflow/profile/', views.queue_profile, name='queue_profile'),
    
    # Settings
    path('settings/questionnaire/', views.settings_questionnaire, name='settings_questionnaire'),
    path('settings/vitals/', views.settings_vitals, name='settings_vitals'),
    path('settings/contraindications/', views.settings_contraindications, name='settings_contraindications'),
    path('settings/deferral/', views.settings_deferral, name='settings_deferral'),
    path('settings/modifications/', views.modification_requests_list, name='modification_requests'),
    path('settings/add-component-manual/', views.add_component_manual, name='add_component_manual'),
    path('reports/donation-certificate/', views.donation_certificate_report, name='donation_certificate'),
    path('workflow/questionnaire/', views.queue_questionnaire, name='queue_questionnaire'),
    path('workflow/questionnaire/failed/', views.questionnaire_failed_list, name='queue_questionnaire_failed'),
    path('workflow/vitals/', views.queue_vitals, name='queue_vitals'),
    path('workflow/collection/', views.queue_collection, name='queue_collection'),
    path('workflow/blood-drawn/', views.blood_drawn_completed_list, name='blood_drawn_completed'),
    
    # Labs
    path('labs/', views.lab_dashboard, name='lab-dashboard'),
    path('labs/infinity/', views.infinity_list, name='infinity-list'),
    path('labs/ortho/', views.ortho_list, name='ortho-list'),
    
    # Donations List
    path('donations/', views.donation_list, name='donation_list'),
    
    # Reports
    path('reports/patient-donors/', views.patient_donors_report, name='patient_donors_report'),
    path('reports/pending-verification/', views.pending_verification, name='pending_verification'),
    path('reports/disposition-to-store/', views.disposition_to_store, name='disposition_to_store'),
    path('reports/store/', views.store_report, name='store_report'),
    path('reports/discarded-units/', views.discarded_units, name='discarded_units'),
    path('reports/expired-units/', views.expired_units, name='expired_units'),
    path('reports/cryo-units/', views.cryo_units, name='cryo_units'),
    path('reports/component-culture/', views.component_culture, name='component_culture'),
    path('reports/patient-bg-discrepancy/', views.patient_bg_discrepancy, name='patient_bg_discrepancy'),
    path('reports/discrepancy-alarms/', views.discrepancy_alarms, name='discrepancy_alarms'),
    
    # New Reports Module
    path('reports/monthly-report/', views.monthly_report, name='monthly_report'),
    path('reports/inventory-checkup/', views.inventory_checkup, name='inventory_checkup'),
    path('reports/component-near-expired/', views.component_near_expired, name='component_near_expired'),
    path('reports/issued-units-summary/', views.issued_units_summary, name='issued_units_summary'),
    path('reports/ortho-summary/', views.ortho_summary, name='ortho_summary'),

    path('reports/component-culture/<str:request_id>/', views.component_culture_view, name='component_culture_view'),
    path('reports/component-details/', views.component_details, name='component_details'),
    
    # Emergency Issue
    path('requests/emergency-issue/', views.emergency_issue_list, name='emergency_issue_list'),
    path('requests/emergency-issue/new/', views.emergency_issue_create, name='emergency_issue_create'),

    # Component Label API (called from Labeling tab in workflow)
    path('api/components/<int:component_id>/print_label/', component_print_label, name='component_print_label'),
    path('api/workflows/<int:workflow_id>/complete_labeling/', complete_labeling, name='complete_labeling'),

    # Lab Results Module
    path('results/ortho-smc1/', views.ortho_results_smc1, name='ortho_results_smc1'),
    path('results/ortho-smc2/', views.ortho_results_smc2, name='ortho_results_smc2'),
    path('results/infinity/', views.infinity_results, name='infinity_results'),
    
    # Blood Order Process
    path('blood-order/requests-old/', views.blood_requests_old, name='blood_requests_old'),
    path('blood-order/requests-old/new/', views.blood_request_create, name='blood_request_create'),
    path('blood-order/listing-bb/', views.blood_order_listing_bb, name='blood_order_listing_bb'),
    path('blood-order/detail/<str:order_code>/', views.blood_order_detail, name='blood_order_detail'),
    path('blood-order/smc2-listing/', views.smc2_orders_listing, name='smc2_orders_listing'),
    path('blood-order/transfusion-orders/', views.transfusion_orders, name='transfusion_orders'),
    path('blood-order/unit-crossmatch/', views.unit_crossmatch_report, name='unit_crossmatch_report'),
    path('blood-order/crossmatch/<int:order_id>/', views.crossmatch_unit, name='crossmatch_unit'),
    path('blood-order/dispense/<int:crossmatch_id>/', views.dispense_unit, name='dispense_unit'),
]
# Force reload 2
# Force reload
