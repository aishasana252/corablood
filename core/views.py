from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout

@login_required # Protect it, requiring login
def dashboard(request):
    return render(request, 'dashboard.html')

def custom_logout(request):
    logout(request)
    return redirect('login')
