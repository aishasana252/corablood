from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from core.decorators import staff_required
from django.db.models import Count, Q
from .models import BloodComponent

@staff_required
def stock_dashboard(request):
    # Aggregation
    stats = BloodComponent.objects.values('component_type', 'status').annotate(count=Count('id'))
    
    # Process into struct
    # Result: {'PRBC': {'AVAILABLE': 10, 'QUARANTINE': 5}, ...}
    stock = {}
    total_available = 0
    
    for s in stats:
        ctype = s['component_type']
        status = s['status']
        count = s['count']
        
        if ctype not in stock:
            stock[ctype] = {'total': 0, 'AVAILABLE': 0, 'QUARANTINE': 0, 'DISCARDED': 0, 'EXPIRED': 0}
            
        stock[ctype][status] = count
        stock[ctype]['total'] += count
        
        if status == 'AVAILABLE':
            total_available += count
            
    recent_units = BloodComponent.objects.select_related('workflow__donor').order_by('-manufactured_at')[:10]
    
    return render(request, 'inventory/stock_dashboard.html', {
        'stock': stock,
        'total_available': total_available,
        'recent_units': recent_units
    })

@staff_required
def separation_dashboard(request):
    return render(request, 'inventory/separation.html')

@staff_required
def processing_rules(request):
    return render(request, 'dashboard.html') # Stub
