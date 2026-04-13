import os

# The corrected view function
CORRECT_VIEW = """@login_required
def settings_contraindications(request):
    from .models import EligibilityRule, DeferralReason, CollectionConfig, ProductSeparationRule
    
    # Load Config
    config, _ = CollectionConfig.objects.get_or_create(pk=1)
    
    if request.method == 'POST':
        action = request.POST.get('action') # 'rule_save' or 'config_save'
        
        if action == 'config_save':
            # Workflow Controls
            config.enable_pre_donation_checks = request.POST.get('enable_pre_donation_checks') == 'on'
            config.require_bag_inspection = request.POST.get('require_bag_inspection') == 'on'
            config.require_arm_inspection = request.POST.get('require_arm_inspection') == 'on'
            config.allow_manual_time_entry = request.POST.get('allow_manual_time_entry') == 'on'
            
            # Stages
            config.enable_separation_stage = request.POST.get('enable_separation_stage') == 'on'
            config.enable_initial_label_stage = request.POST.get('enable_initial_label_stage') == 'on'
            config.enable_untested_storage_stage = request.POST.get('enable_untested_storage_stage') == 'on'
            config.enable_notifications_stage = request.POST.get('enable_notifications_stage') == 'on'
            
            config.save()
            messages.success(request, "Workflow settings updated.")
            return redirect('settings_contraindications')

        elif action == 'separation_rule_save':
            s_id = request.POST.get('separation_rule_id')
            
            defaults = {
                'name': request.POST.get('name'),
                'component_type': request.POST.get('component_type'),
                'min_volume_ml': request.POST.get('min_volume_ml') or 0,
                'max_volume_ml': request.POST.get('max_volume_ml') or 0,
                'centrifuge_program': request.POST.get('centrifuge_program'),
                'expiration_hours': request.POST.get('expiration_hours') or 0,
                'is_active': True 
            }
            
            if s_id:
                ProductSeparationRule.objects.filter(pk=s_id).update(**defaults)
                messages.success(request, "Separation rule updated.")
            else:
                ProductSeparationRule.objects.create(**defaults)
                messages.success(request, "New separation rule created.")
            
            return redirect('settings_contraindications')

        elif action == 'separation_rule_delete':
            s_id = request.POST.get('separation_rule_id')
            ProductSeparationRule.objects.filter(pk=s_id).delete()
            messages.success(request, "Separation rule deleted.")
            return redirect('settings_contraindications')

        else:
            # Rule Save Logic (Existing)
            rule_id = request.POST.get('rule_id')
            min_val = request.POST.get('min_value')
            max_val = request.POST.get('max_value')
            
            # Deferral Params
            deferral_code = request.POST.get('deferral_code')
            deferral_type = request.POST.get('deferral_type') # 'PERMANENT' or 'TEMPORARY'
            days = request.POST.get('deferral_days', 0)
            
            rule = get_object_or_404(EligibilityRule, pk=rule_id)
            
            if min_val: rule.min_value = min_val
            if max_val: rule.max_value = max_val
            
            # Update Deferral config
            if deferral_code:
                rule.deferral_code = deferral_code
                rule.is_permanent_deferral = (deferral_type == 'PERMANENT')
                rule.deferral_days = int(days) if days else 0
                
                # Sync with central DeferralSettings
                DeferralReason.objects.update_or_create(
                    code=deferral_code,
                    defaults={
                        'reason_en': f"Violation of {rule.name}",
                        'reason_ar': f"مخالفة {rule.name}",
                        'is_permanent': rule.is_permanent_deferral,
                        'default_duration_days': rule.deferral_days
                    }
                )
                messages.success(request, f"Updated rule & synced deferral: {rule.name}")
            else:
                messages.success(request, f"Updated rule: {rule.name}")
                
            rule.save()
            return redirect('settings_contraindications')

    rules = EligibilityRule.objects.all()
    separation_rules = ProductSeparationRule.objects.all()
    return render(request, 'clinical/settings_contraindications.html', {
        'rules': rules, 
        'config': config,
        'separation_rules': separation_rules
    })
"""

# Read the file
with open('clinical/views.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

start_index = -1
end_index = -1

# Find the block bounds
for i, line in enumerate(lines):
    if line.strip().startswith('def settings_contraindications(request):'):
        start_index = i - 1 # Include decorator
    if line.strip().startswith('class VitalLimitViewSet(viewsets.ModelViewSet):'):
        end_index = i
        break

if start_index != -1 and end_index != -1:
    new_lines = lines[:start_index] + [CORRECT_VIEW + "\n\n"] + lines[end_index:]
    
    with open('clinical/views.py', 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    print("SUCCESS")
else:
    print("FAILED: Could not find function bounds")
