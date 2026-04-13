
NEW_VIEWS = """

@login_required
def questionnaire_failed_list(request):
    # Donors who were deferred specifically during Questionnaire
    # Ideally tracked by 'status=DEFERRED' AND 'last_step=QUESTIONNAIRE' 
    # For now, we show all DEFERRED workflows for simplicity, or we can refine logic later
    workflows = DonorWorkflow.objects.filter(status=DonorWorkflow.Step.DEFERRED).order_by('-updated_at')
    
    return render(request, 'workflow/queue_questionnaire_failed.html', {
        'workflows': workflows,
        'queue_step': 'DEFERRED'
    })

@login_required
def blood_drawn_completed_list(request):
    # Donors who completed Blood Draw (waiting for Labs or just historical log)
    # Status is typically 'LABS' or 'COMPLETED' if just finished draw
    # Or specifically successful blood draws.
    workflows = DonorWorkflow.objects.filter(status__in=[DonorWorkflow.Step.LABS, DonorWorkflow.Step.COMPLETED]).select_related('blood_draw', 'donor').order_by('-updated_at')
    
    return render(request, 'workflow/blood_drawn_completed.html', {
        'workflows': workflows,
        'queue_step': 'COMPLETED_DRAW'
    })
"""

with open('clinical/views.py', 'a', encoding='utf-8') as f:
    f.write(NEW_VIEWS)
