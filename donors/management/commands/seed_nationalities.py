from donors.models import Nationality

defaults = [
    ('Saudi Arabia', 'المملكة العربية السعودية', True),
    ('Egypt', 'جمهورية مصر العربية', False),
    ('Philippines', 'الفلبين', False),
    ('India', 'الهند', False),
    ('Pakistan', 'باكستان', False),
    ('Yemen', 'اليمن', False),
    ('Jordan', 'الأردن', False),
    ('Sudan', 'السودان', False),
    ('Syria', 'سوريا', False),
    ('Bangladesh', 'بنجلاديش', False),
]

for name_en, name_ar, is_default in defaults:
    Nationality.objects.get_or_create(
        name_en=name_en,
        defaults={
            'name_ar': name_ar,
            'is_default': is_default,
            'is_active': True
        }
    )

print("Nationalities seeded successfully.")
