from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """Admin configuration for CustomUser model"""
    
    list_display = ('username', 'email', 'business_name', 'business_type', 'is_verified', 'is_active', 'created_at')
    list_filter = ('business_type', 'is_verified', 'is_active', 'created_at')
    search_fields = ('username', 'email', 'business_name', 'phone_number')
    ordering = ('-created_at',)
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Business Information', {
            'fields': (
                'business_name', 'business_type', 'phone_number',
                'address_line1', 'address_line2', 'city', 'state', 'zip_code',
                'tax_id', 'business_license'
            )
        }),
        ('Permissions', {
            'fields': (
                'is_active', 'is_staff', 'is_superuser', 'is_verified',
                'groups', 'user_permissions'
            ),
        }),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'username', 'email', 'password1', 'password2',
                'business_name', 'business_type', 'phone_number'
            ),
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at')
