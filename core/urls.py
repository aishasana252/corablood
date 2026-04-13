from django.urls import path
from django.contrib.auth import views as auth_views
from django.views.generic import RedirectView
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    
    # Custom Logout to accept GET requests without 405 error (especially helpful if users manually type /logout/)
    path('logout/', views.custom_logout, name='logout'),
    
    path('accounts/login/', RedirectView.as_view(url='/login/')), # Catch-all 
]

