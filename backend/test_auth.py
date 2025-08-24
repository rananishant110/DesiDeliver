#!/usr/bin/env python3
"""
Simple test script to verify DesiDeliver authentication endpoints
"""

import requests
import json

BASE_URL = "http://127.0.0.1:8000/api/auth"

def test_registration():
    """Test user registration"""
    print("Testing User Registration...")
    
    registration_data = {
        "username": "testrestaurant",
        "email": "test@restaurant.com",
        "password": "TestPass123!",
        "password_confirm": "TestPass123!",
        "first_name": "Test",
        "last_name": "Restaurant",
        "business_name": "Test Indian Restaurant",
        "business_type": "restaurant",
        "phone_number": "+1234567890",
        "address_line1": "123 Test Street",
        "city": "Dallas",
        "state": "TX",
        "zip_code": "75201"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/register/", json=registration_data)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 201:
            data = response.json()
            print("✅ Registration successful!")
            print(f"User ID: {data['user']['id']}")
            print(f"Business: {data['user']['business_name']}")
            print(f"Token: {data['token'][:20]}...")
            return data['token']
        else:
            print("❌ Registration failed!")
            print(f"Response: {response.text}")
            return None
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection failed! Make sure Django server is running.")
        return None
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return None

def test_login():
    """Test user login"""
    print("\nTesting User Login...")
    
    login_data = {
        "username": "testrestaurant",
        "password": "TestPass123!"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/login/", json=login_data)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Login successful!")
            print(f"User: {data['user']['username']}")
            print(f"Business: {data['user']['business_name']}")
            print(f"Token: {data['token'][:20]}...")
            return data['token']
        else:
            print("❌ Login failed!")
            print(f"Response: {response.text}")
            return None
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection failed! Make sure Django server is running.")
        return None
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return None

def test_profile(token):
    """Test user profile access"""
    if not token:
        print("❌ No token available for profile test")
        return
    
    print("\nTesting User Profile Access...")
    
    headers = {
        "Authorization": f"Token {token}"
    }
    
    try:
        response = requests.get(f"{BASE_URL}/profile/", headers=headers)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Profile access successful!")
            print(f"Username: {data['username']}")
            print(f"Business: {data['business_name']}")
            print(f"Business Type: {data['business_type']}")
            print(f"Verified: {data['is_verified']}")
        else:
            print("❌ Profile access failed!")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection failed! Make sure Django server is running.")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def test_dashboard(token):
    """Test user dashboard access"""
    if not token:
        print("❌ No token available for dashboard test")
        return
    
    print("\nTesting User Dashboard Access...")
    
    headers = {
        "Authorization": f"Token {token}"
    }
    
    try:
        response = requests.get(f"{BASE_URL}/dashboard/", headers=headers)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Dashboard access successful!")
            print(f"User: {data['user']['username']}")
            print(f"Business: {data['business_info']['business_name']}")
            print(f"Address: {data['business_info']['address']}")
        else:
            print("❌ Dashboard access failed!")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection failed! Make sure Django server is running.")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def main():
    """Run all tests"""
    print("🚀 DesiDeliver Authentication System Test")
    print("=" * 50)
    
    # Test registration
    token = test_registration()
    
    # Test login
    login_token = test_login()
    
    # Test profile with registration token
    if token:
        test_profile(token)
    
    # Test dashboard with login token
    if login_token:
        test_dashboard(login_token)
    
    print("\n" + "=" * 50)
    print("🏁 Test completed!")

if __name__ == "__main__":
    main()
