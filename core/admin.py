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
        # Exclude donors from the system users list as requested by the user
        return qs.exclude(role__iexact='Donor')

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
