from django.urls import path
from . import views

urlpatterns = [
    path('stock/', views.stock_dashboard, name='stock-dashboard'),
    path('separation/', views.separation_dashboard, name='separation-dashboard'),
    path('processing-rules/', views.processing_rules, name='processing_rules'),
]
