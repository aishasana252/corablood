from clinical.models import EligibilityRule

rules = [
    # Demographics
    {
        'name': 'Age (Years)',
        'key': 'age',
        'category': 'DEMOGRAPHICS',
        'min': 18,
        'max': 65,
        'gender': 'ANY',
        'order': 1
    },
    {
        'name': 'Weight (KG)',
        'key': 'weight',
        'category': 'DEMOGRAPHICS',
        'min': 50,
        'max': 200,
        'gender': 'ANY',
        'order': 2
    },
    # Vitals
    {
        'name': 'Temperature (°C)',
        'key': 'temp',
        'category': 'VITALS',
        'min': 36.0,
        'max': 37.5,
        'gender': 'ANY',
        'order': 3
    },
    {
        'name': 'Pulse (BPM)',
        'key': 'pulse',
        'category': 'VITALS',
        'min': 50,
        'max': 100,
        'gender': 'ANY',
        'order': 4
    },
    {
        'name': 'Systolic BP (mmHg)',
        'key': 'bp_systolic',
        'category': 'VITALS',
        'min': 90,
        'max': 180,
        'gender': 'ANY',
        'order': 5
    },
    {
        'name': 'Diastolic BP (mmHg)',
        'key': 'bp_diastolic',
        'category': 'VITALS',
        'min': 50,
        'max': 100,
        'gender': 'ANY',
        'order': 6
    },
    # Labs (HGB)
    {
        'name': 'Hemoglobin (Male)',
        'key': 'hgb_male',
        'category': 'LABS',
        'min': 13.0,
        'max': 17.0,
        'gender': 'M',
        'order': 7
    },
    {
        'name': 'Hemoglobin (Female)',
        'key': 'hgb_female',
        'category': 'LABS',
        'min': 12.5,
        'max': 16.0,
        'gender': 'F',
        'order': 8
    },
    # Platelets (Pre-Apherisis)
    {
        'name': 'Platelet Count (Pre-Apheresis)',
        'key': 'plt_pre',
        'category': 'LABS',
        'min': 150,
        'max': 450,
        'gender': 'ANY',
        'order': 9
    }
]

for r in rules:
    EligibilityRule.objects.update_or_create(
        key=r['key'],
        defaults={
            'name': r['name'],
            'category': r['category'],
            'min_value': r['min'],
            'max_value': r['max'],
            'gender': r['gender'],
            'order': r['order'],
            'is_active': True
        }
    )

print("Eligibility Rules seeded.")
