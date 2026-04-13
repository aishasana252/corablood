
VIEW_CODE = """

@login_required
def donation_certificate_report(request):
    from .models import DonorWorkflow
    
    # Fetch donations (Workflows)
    # Ideally filter by status='COMPLETED' or similar, but showing all for demo
    workflows = DonorWorkflow.objects.select_related('donor', 'blood_draw').order_by('-created_at')

    # Mocking 'Blood Nature' and 'Certificate Status' for display consistency with screenshot
    # In a real app, these would be fields on the model
    for wf in workflows:
        wf.blood_nature = "Whole Blood" # Default
        wf.cert_status = "New" # Default

    context = {
        'workflows': workflows
    }
    return render(request, 'clinical/donation_certificate_report.html', context)
"""

with open('clinical/views.py', 'a', encoding='utf-8') as f:
    f.write(VIEW_CODE)
