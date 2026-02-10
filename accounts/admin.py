"""
Admin site configuration for user management.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User
from .forms import CustomUserCreationForm, CustomUserChangeForm


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """
    Custom admin configuration for the User model.
    """
    
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = User
    
    list_display = (
        'username', 'email', 'first_name', 'last_name',
        'role', 'employee_id', 'is_active', 'date_joined'
    )
    list_filter = (
        'role', 'is_active', 'is_staff', 'date_joined',
        'last_login'
    )
    search_fields = (
        'username', 'email', 'first_name', 'last_name',
        'employee_id', 'library_card_number'
    )
    ordering = ('-date_joined',)
    
    readonly_fields = (
        'date_joined', 'last_login', 'password_changed_at',
        'last_login_ip'
    )
    
    fieldsets = (
        ('Personal Info', {
            'fields': (
                'username', 'email', 'first_name', 'last_name',
                'date_of_birth'
            )
        }),
        ('Employment Info', {
            'fields': (
                'role', 'employee_id', 'department',
                'phone_number', 'library_card_number'
            )
        }),
        ('Permissions', {
            'fields': (
                'is_active', 'is_staff', 'is_superuser',
                'can_upload', 'can_delete', 'can_manage_users',
                'can_view_all_documents',
                'user_permissions'
            )
        }),
        ('Security', {
            'fields': (
                'password', 'password_changed_at',
                'account_expires_at', 'last_login_ip'
            )
        }),
        ('Important Dates', {
            'fields': ('date_joined', 'last_login')
        }),
    )
    
    add_fieldsets = (
        ('Personal Info', {
            'fields': (
                'username', 'email', 'first_name', 'last_name',
                'password1', 'password2'
            )
        }),
        ('Employment Info', {
            'fields': (
                'role', 'employee_id', 'department',
                'phone_number', 'library_card_number'
            )
        }),
        ('Permissions', {
            'fields': (
                'is_active', 'can_upload', 'can_delete',
                'can_manage_users', 'can_view_all_documents'
            )
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request)
    
    def has_delete_permission(self, request, obj=None):
        # Prevent deletion of superuser
        if obj and obj.is_superuser:
            return False
        return super().has_delete_permission(request, obj)
    
    def get_readonly_fields(self, request, obj=None):
        readonly = list(super().get_readonly_fields(request, obj))
        
        # Prevent users from demoting themselves
        if obj == request.user:
            readonly.extend(['is_active', 'is_staff', 'is_superuser'])
        
        return readonly
