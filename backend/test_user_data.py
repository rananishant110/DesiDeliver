#!/usr/bin/env python
"""
Test script to check user data returned by API
Run this to see what fields are available for the user
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

def check_user_data():
    """Check what user data is available"""
    
    print("🔍 Checking User Data Structure...")
    
    try:
        # Get all users
        users = CustomUser.objects.all()
        
        print(f"\n📊 Total Users: {users.count()}")
        
        for user in users:
            print(f"\n👤 User: {user.username}")
            print(f"   Email: {user.email}")
            print(f"   Business Name: {user.business_name}")
            print(f"   Is Staff: {user.is_staff}")
            print(f"   Is Superuser: {user.is_superuser}")
            print(f"   Is Active: {user.is_active}")
            print(f"   Date Joined: {user.date_joined}")
            
            # Check all available fields
            print(f"   All Fields: {[field.name for field in user._meta.fields]}")
            
            # Check if is_staff is in the model
            if hasattr(user, 'is_staff'):
                print(f"   ✅ is_staff field exists: {user.is_staff}")
            else:
                print(f"   ❌ is_staff field missing!")
        
        # Check the model definition
        print(f"\n🏗️ CustomUser Model Fields:")
        for field in CustomUser._meta.fields:
            print(f"   - {field.name}: {field.__class__.__name__}")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    check_user_data()
