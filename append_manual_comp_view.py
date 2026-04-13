
VIEW_CODE = """

@login_required
def add_component_manual(request):
    from .models import ProductSeparationRule
    
    # Choices for dropdowns
    component_types = ProductSeparationRule.Component.choices
    blood_groups = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']
    sources = ['In-House', 'External Drive', 'Imported']
    sites = ['Main Center', 'Mobile Unit 1', 'Mobile Unit 2']

    if request.method == 'POST':
        # Logic to save connection (placeholder for now as no ManualComponent model exists yet)
        messages.success(request, "Manual component added successfully (Simulation).")
        return redirect('add_component_manual')

    return render(request, 'clinical/add_component_manual.html', {
        'component_types': component_types,
        'blood_groups': blood_groups,
        'sources': sources,
        'sites': sites
    })
"""

with open('clinical/views.py', 'a', encoding='utf-8') as f:
    f.write(VIEW_CODE)
