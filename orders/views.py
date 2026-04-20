from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from core.decorators import staff_required
from django.contrib import messages
from .models import BloodOrder, Crossmatch
from .services import OrderService
from inventory.models import BloodComponent

@staff_required
def order_list(request):
    orders = BloodOrder.objects.all().order_by('-created_at')
    return render(request, 'orders/list.html', {'orders': orders})

@staff_required
def create_order(request):
    if request.method == 'POST':
        data = {
            'patient_mrn': request.POST.get('patient_mrn'),
            'patient_full_name': request.POST.get('patient_full_name'),
            'patient_blood_group': request.POST.get('patient_blood_group'),
            'hospital_ward': request.POST.get('hospital_ward'),
            'component_type': request.POST.get('component_type'),
            'units_requested': int(request.POST.get('units_requested')),
            'urgency': request.POST.get('urgency'),
        }
        OrderService.create_order(data, request.user)
        messages.success(request, "Order Created")
        return redirect('order_list')
        
    return render(request, 'orders/create.html')

@staff_required
def order_detail(request, pk):
    order = get_object_or_404(BloodOrder, pk=pk)
    # Suggestions
    suggestions = OrderService.find_compatible_units(order)
    return render(request, 'orders/detail.html', {'order': order, 'suggestions': suggestions})

@staff_required
def crossmatch_action(request, order_id, unit_id):
    if request.method == 'POST':
        order = get_object_or_404(BloodOrder, pk=order_id)
        unit = get_object_or_404(BloodComponent, pk=unit_id)
        
        xm = OrderService.perform_crossmatch(order, unit, request.user)
        
        if xm.is_compatible:
            messages.success(request, f"Unit {unit.unit_number} Compatible & Reserved")
        else:
            messages.error(request, f"Unit {unit.unit_number} INCOMPATIBLE")
            
        return redirect('order_detail', pk=order_id)

@login_required
def dispense_action(request, xm_id):
    if request.method == 'POST':
        xm = get_object_or_404(Crossmatch, pk=xm_id)
        OrderService.dispense_unit(xm, request.user)
        messages.success(request, f"Unit {xm.unit.unit_number} Dispensed Successfully")
        return redirect('order_list')
