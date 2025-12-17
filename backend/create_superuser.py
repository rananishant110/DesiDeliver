#!/usr/bin/env python
"""
Script to create a superuser with predefined credentials
"""

import os
import sys
import django

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'desideliver_backend.settings')
django.setup()

from users.models import CustomUser

def create_superuser():
    """Create a superuser with predefined credentials"""
    
    username = 'admin'
    email = 'admin@desideliver.com'
    password = 'admin123'
    
    try:
        # Check if user already exists
        if CustomUser.objects.filter(username=username).exists():
            user = CustomUser.objects.get(username=username)
            user.set_password(password)
            user.save()
            print(f"✅ Updated existing superuser: {username}")
        else:
            user = CustomUser.objects.create_superuser(
                username=username,
                email=email,
                password=password,
                business_name='DesiDeliver Admin',
                phone_number='1234567890'
            )
            print(f"✅ Created new superuser: {username}")
        
        print(f"\n🔐 Superuser Credentials:")
        print(f"   Username: {username}")
        print(f"   Email: {email}")
        print(f"   Password: {password}")
        print(f"\n🌐 Access admin at: http://127.0.0.1:8000/admin/")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    create_superuser()
