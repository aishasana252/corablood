import os

VIEW_CODE = """

@login_required
def settings_deferral(request):
    from .models import DeferralReason
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'save':
            d_id = request.POST.get('id')
            defaults = {
                'code': request.POST.get('code') or f"DEF-{DeferralReason.objects.count() + 100}", 
                'reason_en': request.POST.get('title_en'),
                'reason_ar': request.POST.get('title_ar'),
                'description_en': request.POST.get('desc_en'),
                'description_ar': request.POST.get('desc_ar'),
                'default_duration_days': int(request.POST.get('blocking_days') or 0),
                'deferral_type': request.POST.get('type'),
                'is_active': request.POST.get('is_active') == 'on'
            }
            
            if d_id:
                DeferralReason.objects.filter(pk=d_id).update(**defaults)
                messages.success(request, "Deferral reason updated.")
            else:
                DeferralReason.objects.create(**defaults)
                messages.success(request, "New deferral reason added.")
                
        elif action == 'delete':
            d_id = request.POST.get('id')
            DeferralReason.objects.filter(pk=d_id).delete()
            messages.success(request, "Deferral reason deleted.")
            
        return redirect('settings_deferral')

    deferrals = DeferralReason.objects.all().order_by('-id')
    return render(request, 'clinical/settings_deferral.html', {'deferrals': deferrals})
"""

with open('clinical/views.py', 'a', encoding='utf-8') as f:
    f.write(VIEW_CODE)
