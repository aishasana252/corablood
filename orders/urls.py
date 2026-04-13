from django.urls import path
from . import views

urlpatterns = [
    path('', views.order_list, name='order_list'),
    path('new/', views.create_order, name='create_order'),
    path('<int:pk>/', views.order_detail, name='order_detail'),
    path('<int:order_id>/crossmatch/<int:unit_id>/', views.crossmatch_action, name='crossmatch_action'),
    path('dispense/<int:xm_id>/', views.dispense_action, name='dispense_action'),
]
