from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from donors.models import Donor


@login_required(login_url='portal:login')
def portal_profile(request):
    if request.user.role != 'Donor':
        return redirect('login')

    try:
        donor = request.user.donor_profile
    except:
        messages.error(request, "Donor profile not found.")
        return redirect('portal:dashboard')

    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        mobile = request.POST.get('mobile')
        dob = request.POST.get('dob')
        email = request.POST.get('email')
        blood_type = request.POST.get('blood_type')

        if not full_name or not mobile or not dob:
            messages.error(request, "Required fields cannot be empty.")
            return redirect('portal:profile')

        try:
            donor.full_name = full_name
            donor.mobile = mobile
            donor.dob = dob
            donor.email = email
            donor.blood_group = blood_type
            donor.save()

            request.user.email = email
            request.user.save()

            messages.success(request, "Profile updated successfully.")
            return redirect('portal:profile')
        except Exception as e:
            messages.error(request, f"Error updating profile: {str(e)}")

    return render(request, 'donors/portal/profile.html', {'donor': donor})
