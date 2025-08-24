from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator

class CustomUser(AbstractUser):
    """
    Custom user model for DesiDeliver application.
    Extends Django's AbstractUser to include business information.
    """
    
    # Business Information
    business_name = models.CharField(max_length=200, blank=True)
    business_type = models.CharField(
        max_length=50,
        choices=[
            ('restaurant', 'Restaurant'),
            ('store', 'Store'),
            ('catering', 'Catering'),
            ('other', 'Other'),
        ],
        default='restaurant'
    )
    
    # Contact Information
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
    )
    phone_number = models.CharField(validators=[phone_regex], max_length=17, blank=True)
    
    # Address Information
    address_line1 = models.CharField(max_length=255, blank=True)
    address_line2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=50, blank=True)
    zip_code = models.CharField(max_length=10, blank=True)
    
    # Business Details
    tax_id = models.CharField(max_length=50, blank=True)
    business_license = models.CharField(max_length=100, blank=True)
    
    # Account Status
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        db_table = 'users'
    
    def __str__(self):
        return f"{self.business_name} ({self.username})" if self.business_name else self.username
    
    def get_full_address(self):
        """Return formatted full address"""
        address_parts = []
        if self.address_line1:
            address_parts.append(self.address_line1)
        if self.address_line2:
            address_parts.append(self.address_line2)
        if self.city:
            address_parts.append(self.city)
        if self.state:
            address_parts.append(self.state)
        if self.zip_code:
            address_parts.append(self.zip_code)
        return ', '.join(address_parts) if address_parts else 'No address provided'
    
    def get_business_info(self):
        """Return business information summary"""
        return {
            'business_name': self.business_name,
            'business_type': self.business_type,
            'phone_number': self.phone_number,
            'address': self.get_full_address(),
            'is_verified': self.is_verified
        }
