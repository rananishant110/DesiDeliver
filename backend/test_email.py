#!/usr/bin/env python
"""
Test script for email functionality
Run this script to test email sending capabilities
"""

import os
import sys
import django
from datetime import datetime

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'desideliver_backend.settings')
django.setup()

from orders.models import Order, OrderItem
from products.models import Product, Category
from users.models import CustomUser
from orders.email_service import EmailService

def test_email_functionality():
    """Test the email service with a sample order"""
    
    print("🧪 Testing Email Service...")
    
    try:
        # Get or create a test user
        user, created = CustomUser.objects.get_or_create(
            username='testuser',
            defaults={
                'email': 'test@example.com',
                'business_name': 'Test Restaurant',
                'contact_person': 'John Doe',
                'phone_number': '555-1234'
            }
        )
        
        if created:
            user.set_password('testpass123')
            user.save()
            print(f"✅ Created test user: {user.username}")
        else:
            print(f"✅ Using existing test user: {user.username}")
        
        # Get or create a test category
        category, created = Category.objects.get_or_create(
            name='Test Category',
            defaults={'description': 'Test category for email testing'}
        )
        
        if created:
            print(f"✅ Created test category: {category.name}")
        else:
            print(f"✅ Using existing test category: {category.name}")
        
        # Get or create a test product
        product, created = Product.objects.get_or_create(
            item_code='TEST001',
            defaults={
                'name': 'Test Product',
                'description': 'Test product for email testing',
                'category': category,
                'unit': 'g',
                'stock_quantity': 100
            }
        )
        
        if created:
            print(f"✅ Created test product: {product.name}")
        else:
            print(f"✅ Using existing test product: {product.name}")
        
        # Create a test order
        order = Order.objects.create(
            customer=user,
            delivery_address='123 Test Street, Dallas, TX 75201',
            delivery_instructions='Ring doorbell twice',
            business_name='Test Restaurant',
            contact_person='John Doe',
            phone_number='555-1234'
        )
        
        # Create order item
        OrderItem.objects.create(
            order=order,
            product=product,
            quantity=5
        )
        
        # Update order total
        order.total_items = 5
        order.save()
        
        print(f"✅ Created test order: {order.order_number}")
        
        # Test email service
        email_service = EmailService()
        
        print("\n📧 Testing Customer Order Confirmation Email...")
        customer_success = email_service.send_order_confirmation_email(
            order, user.email
        )
        
        if customer_success:
            print("✅ Customer order confirmation email sent successfully!")
        else:
            print("❌ Failed to send customer order confirmation email")
        
        print("\n📧 Testing Delivery Coordinator Notification...")
        coordinator_success = email_service.send_delivery_coordinator_notification(order)
        
        if coordinator_success:
            print("✅ Delivery coordinator notification sent successfully!")
        else:
            print("❌ Failed to send delivery coordinator notification")
        
        print("\n📧 Testing Daily Summary Email...")
        daily_success = email_service.send_daily_orders_summary(
            [order], datetime.now().strftime('%B %d, %Y')
        )
        
        if daily_success:
            print("✅ Daily summary email sent successfully!")
        else:
            print("❌ Failed to send daily summary email")
        
        # Clean up test data
        print("\n🧹 Cleaning up test data...")
        order.delete()
        product.delete()
        category.delete()
        user.delete()
        print("✅ Test data cleaned up")
        
        print("\n🎉 Email testing completed!")
        
    except Exception as e:
        print(f"❌ Error during email testing: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_email_functionality()
