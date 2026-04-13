from django.urls import reverse

# Define the tools available to Gemini
# We use standard Python docstrings and type hints to help Gemini understand the tools

def navigate_to_page(page_name: str) -> dict:
    """
    Navigates the user to a specific page in the application.
    
    Args:
        page_name: The logical name of the page to navigate to. Supported values:
            - 'dashboard': The main admin dashboard (/dashboard/)
            - 'donors_list': The list of all registered donors (/donors/list/)
            - 'add_donor': Registration page for a new donor (/donors/add/)
            - 'inventory': The blood inventory dashboard (/inventory/)
            - 'blood_requests': The hospital blood requests page (/orders/requests/)
    """
    url_mapping = {
        'dashboard': reverse('dashboard'),
        'donors_list': reverse('donors:donor_list'),
        'add_donor': reverse('donors:donor_add'),
        'inventory': reverse('inventory:dashboard'),
        'blood_requests': reverse('orders:blood_request_list'),
    }
    
    target_url = url_mapping.get(page_name.lower())
    
    if target_url:
        return {
            "status": "success",
            "message": f"Navigating to {page_name}",
            "action": "redirect",
            "url": target_url
        }
    else:
        return {
            "status": "error",
            "message": f"Unknown page: {page_name}. Supported pages are: {', '.join(url_mapping.keys())}"
        }

def create_donor_profile(
    national_id: str, 
    full_name: str, 
    date_of_birth: str, 
    gender: str, 
    mobile: str, 
    blood_group: str = 'UNKNOWN',
    nationality: str = 'Saudi Arabia'
) -> dict:
    """
    Creates a new donor profile in the system. Use this when the user asks to add or register a new donor.
    
    Args:
        national_id: The donor's National ID or Iqama number (e.g., '10xxxxxxxx', unique).
        full_name: The donor's full name.
        date_of_birth: The donor's date of birth in 'YYYY-MM-DD' format.
        gender: 'M' for Male, or 'F' for Female.
        mobile: The donor's mobile phone number.
        blood_group: The donor's blood group (e.g., 'A+', 'O-', 'UNKNOWN'). Defaults to 'UNKNOWN'.
        nationality: The donor's nationality. Defaults to 'Saudi Arabia'.
    """
    from donors.models import Donor
    from django.db import IntegrityError
    import datetime

    try:
        # Validate date format
        datetime.datetime.strptime(date_of_birth, '%Y-%m-%d')
        
        # Determine first/last name
        name_parts = full_name.split()
        first_name = name_parts[0] if name_parts else ''
        last_name = name_parts[-1] if len(name_parts) > 1 else ''

        donor = Donor.objects.create(
            national_id=national_id,
            full_name=full_name,
            first_name=first_name,
            last_name=last_name,
            date_of_birth=date_of_birth,
            gender=gender,
            mobile=mobile,
            blood_group=blood_group,
            nationality=nationality
        )
        url = reverse('donors:donor_detail', args=[donor.pk])
        return {
            "status": "success",
            "message": f"Successfully created donor profile for {full_name}.",
            "action": "redirect",
            "url": url,
            "donor_id": donor.id
        }
    except IntegrityError:
        return {
            "status": "error",
            "message": f"A donor with National ID {national_id} already exists."
        }
    except ValueError as e:
        return {
            "status": "error",
            "message": f"Invalid data provided: {str(e)}. Make sure date_of_birth is exactly 'YYYY-MM-DD'."
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to create donor: {str(e)}"
        }

def search_donor(query: str) -> dict:
    """
    Searches for donors matching a query (Name, National ID, or Mobile number).
    
    Args:
        query: The search term. Can be a name, an ID, or a phone number.
    """
    from donors.models import Donor
    from django.db.models import Q
    
    donors = Donor.objects.filter(
        Q(full_name__icontains=query) | 
        Q(national_id__icontains=query) | 
        Q(mobile__icontains=query)
    )[:5]
    
    if not donors:
        return {"status": "not_found", "message": f"No donors found matching '{query}'."}
        
    results = []
    for d in donors:
        results.append({
            "id": d.id,
            "national_id": d.national_id,
            "name": d.full_name,
            "blood_group": d.blood_group,
            "mobile": d.mobile,
            "is_eligible": d.is_eligible,
            "url": reverse('donors:donor_detail', args=[d.id])
        })
        
    return {
        "status": "success",
        "message": f"Found {len(results)} matching donor(s).",
        "donors": results
    }

def update_donor(national_id: str, new_mobile: str = None, new_blood_group: str = None) -> dict:
    """
    Updates an existing donor's information.
    
    Args:
        national_id: The unique National ID or Iqama of the donor to update.
        new_mobile: (Optional) The new mobile number.
        new_blood_group: (Optional) The new blood group (e.g. 'A+', 'O-').
    """
    from donors.models import Donor
    try:
        donor = Donor.objects.get(national_id=national_id)
        changes = []
        if new_mobile:
            donor.mobile = new_mobile
            changes.append(f"mobile '{new_mobile}'")
        if new_blood_group:
            donor.blood_group = new_blood_group
            changes.append(f"blood group '{new_blood_group}'")
            
        if changes:
            donor.save()
            return {
                "status": "success",
                "message": f"Updated donor {donor.full_name}. Changes: {', '.join(changes)}."
            }
        return {"status": "info", "message": "No changes were specified."}
    except Donor.DoesNotExist:
        return {"status": "error", "message": f"Donor with National ID {national_id} not found."}

def defer_donor(national_id: str, reason: str, days: int) -> dict:
    """
    Adds a temporary medical deferral to a donor to block them from donating.
    
    Args:
        national_id: The National ID of the donor.
        reason: The reason for deferral (e.g. 'Low Hemoglobin', 'Recent Surgery').
        days: Number of days to block the donor.
    """
    from donors.models import Donor, DonorDeferral
    import datetime
    try:
        donor = Donor.objects.get(national_id=national_id)
        
        # Calculate end date
        end_date = datetime.date.today() + datetime.timedelta(days=days)
        
        deferral = DonorDeferral.objects.create(
            donor=donor,
            reason=reason,
            deferral_type=DonorDeferral.Type.TEMPORARY,
            days_blocked=days,
            end_date=end_date,
            is_active=True
        )
        
        # Also update the donor's status
        donor.deferral_status = True
        donor.deferral_reason = reason
        donor.deferral_end_date = end_date
        donor.save()
        
        return {
            "status": "success",
            "message": f"Donor {donor.full_name} has been deferred for {days} days due to {reason}.",
            "deferral_id": deferral.id
        }
    except Donor.DoesNotExist:
        return {"status": "error", "message": f"Donor with National ID {national_id} not found."}

def get_inventory_status(component_type: str = None) -> dict:
    """
    Gets the current count of available blood bags in the inventory.
    
    Args:
        component_type: (Optional) Limit search to specific component e.g. 'PRBC', 'FFP', 'PLT'. If null, returns all.
    """
    from inventory.models import BloodComponent
    from django.db.models import Count
    
    query = BloodComponent.objects.filter(status=BloodComponent.Status.AVAILABLE)
    if component_type:
        query = query.filter(component_type__icontains=component_type)
        
    counts = query.values('component_type', 'blood_group').annotate(count=Count('id')).order_by('component_type', 'blood_group')
    
    results = {}
    total = 0
    for item in counts:
        ctype = item['component_type']
        bgroup = item['blood_group']
        cnt = item['count']
        if ctype not in results:
            results[ctype] = {}
        results[ctype][bgroup] = cnt
        total += cnt
        
    if not results:
        return {"status": "success", "message": "The inventory has 0 available blood units.", "total": 0}
        
    return {
        "status": "success",
        "message": f"Found {total} available blood units.",
        "inventory": results,
        "total": total
    }

def create_blood_request(
    patient_name: str, 
    mrn: str, 
    patient_blood_group: str, 
    component_type: str, 
    units: int, 
    urgency: str = 'ROUTINE',
    ward: str = 'ER'
) -> dict:
    """
    Creates a new blood order request for a patient.
    
    Args:
        patient_name: Full name of the patient.
        mrn: Medical Record Number.
        patient_blood_group: Patient's blood group (e.g. 'A+').
        component_type: Type needed (e.g. 'PRBC', 'FFP', 'PLT', 'WB').
        units: Number of units requested.
        urgency: 'ROUTINE', 'URGENT', or 'EMERGENCY'.
        ward: Hospital ward/room. Defaults to 'ER'.
    """
    from orders.models import BloodOrder
    try:
        # Validate component type matching choices
        valid_types = [c[0] for c in BloodOrder._meta.get_field('component_type').choices]
        if component_type.upper() not in valid_types:
            return {"status": "error", "message": f"Invalid component type. Must be one of: {valid_types}"}
            
        valid_urgencies = [c[0] for c in BloodOrder._meta.get_field('urgency').choices]
        if urgency.upper() not in valid_urgencies:
             urgency = 'ROUTINE' # Fallback
            
        order = BloodOrder.objects.create(
            patient_mrn=mrn,
            patient_full_name=patient_name,
            patient_blood_group=patient_blood_group.upper(),
            hospital_ward=ward,
            component_type=component_type.upper(),
            units_requested=units,
            urgency=urgency.upper(),
            status=BloodOrder.Status.PENDING
        )
        url = reverse('orders:blood_request_detail', args=[order.pk])
        return {
            "status": "success",
            "message": f"Successfully created Blood Order #{order.id} for {patient_name} ({units}x {component_type}).",
            "action": "redirect",
            "url": url,
            "order_id": order.id
        }
    except Exception as e:
        return {"status": "error", "message": f"Failed to create order: {str(e)}"}

# List of all available tools to pass to the model
AVAILABLE_TOOLS = [
    navigate_to_page, 
    create_donor_profile, 
    search_donor, 
    update_donor,
    defer_donor,
    get_inventory_status,
    create_blood_request
]
