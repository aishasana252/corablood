from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from django.urls import reverse
from .models import User, SystemSettings

@admin.register(SystemSettings)
class SystemSettingsAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'donor_id_length', 'donor_phone_prefix', 'donor_min_age', 'donor_max_age')
    
    def has_add_permission(self, request):
        return False if self.model.objects.exists() else super().has_add_permission(request)
    
    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'role', 'is_active', 'is_staff', 'edit_action')
    list_filter = ('is_active', 'is_staff')
    search_fields = ('username', 'email', 'role')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # Show all staff/superusers, and any non-donor users. 
        # Hide regular donors who don't have staff status to keep the list clean.
        from django.db.models import Q
        return qs.filter(Q(is_staff=True) | Q(is_superuser=True) | ~Q(role__iexact='Donor'))

    def edit_action(self, obj):
        url = reverse('admin:core_user_change', args=[obj.id])
        return format_html(
            '<a class="btn btn-sm btn-info" style="color: white; padding: 2px 10px; border-radius: 4px;" href="{}"><i class="fas fa-edit"></i> Edit</a>', 
            url
        )
    edit_action.short_description = 'Action'

    fieldsets = (
        ('Login Credentials', {
            'fields': ('username', 'password')
        }),
        ('Personal Information', {
            'fields': ('first_name', 'last_name', 'email')
        }),
        ('Role / Job Title', {
            'fields': ('role',),
            'description': 'Write the job title of this user (e.g. Doctor, Nurse, Lab Technician).'
        }),
        ('Module Access — Tick to Grant Access', {
            'fields': (
                'can_access_dashboard',
                'can_access_donors',
                'can_access_donations',
                'can_access_settings',
                'can_access_inventory',
                'can_access_reports',
                'can_access_clinical',
                'can_access_orders',
                'can_access_ai',
            ),
            'description': 'Select which parts of the system this user is allowed to access.',
        }),
        ('System Access Level', {
            'fields': ('is_active', 'is_staff', 'is_superuser'),
            'description': 'is_active = can login | is_staff = can open admin panel | is_superuser = full access'
        }),
        ('Advanced Permissions', {
            'fields': ('groups', 'user_permissions'),
            'classes': ('collapse',),
        }),
        ('Important Dates', {
            'fields': ('last_login', 'date_joined'),
            'classes': ('collapse',),
        }),
    )

    add_fieldsets = (
        ('Create New User', {
            'classes': ('wide',),
            'fields': (
                'username', 'password1', 'password2',
                'email', 'first_name', 'last_name',
                'role',
                'can_access_dashboard', 'can_access_donors', 'can_access_donations', 
                'can_access_settings', 'can_access_inventory', 'can_access_reports',
                'can_access_clinical', 'can_access_orders', 'can_access_ai',
                'is_active', 'is_staff',
            ),
        }),
    )

    def save_model(self, request, obj, form, change):
        """
        Override save to ensure custom fields are properly saved during user creation.
        Django's UserAdmin sometimes skips custom fields on the 'add' form.
        Also auto-sets is_staff=True if user has any clinical access permissions.
        """
        super().save_model(request, obj, form, change)
        
        if not change:
            # This is a NEW user being created — re-apply custom fields from form data
            custom_fields = [
                'role', 'can_access_dashboard', 'can_access_donors', 'can_access_donations',
                'can_access_settings', 'can_access_inventory', 'can_access_reports',
                'can_access_clinical', 'can_access_orders', 'can_access_ai',
                'is_staff', 'is_active',
            ]
            needs_save = False
            for field in custom_fields:
                if field in form.cleaned_data:
                    current_val = getattr(obj, field, None)
                    new_val = form.cleaned_data[field]
                    if current_val != new_val:
                        setattr(obj, field, new_val)
                        needs_save = True
            
            # Auto-enable is_staff if any clinical access permission is granted
            has_any_access = any([
                obj.can_access_dashboard, obj.can_access_donors, obj.can_access_donations,
                obj.can_access_settings, obj.can_access_inventory, obj.can_access_reports,
                obj.can_access_clinical, obj.can_access_orders,
            ])
            if has_any_access and not obj.is_staff:
                obj.is_staff = True
                needs_save = True
                
            if needs_save:
                obj.save()
