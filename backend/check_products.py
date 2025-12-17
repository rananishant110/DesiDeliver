#!/usr/bin/env python
"""
Script to check if there are products in the database
"""

import os
import sys
import django

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'desideliver_backend.settings')
django.setup()

from products.models import Product, Category

def check_products():
    """Check if there are products in the database"""
    
    print("🔍 Checking Product Database...")
    
    try:
        # Count products and categories
        total_products = Product.objects.count()
        active_products = Product.objects.filter(is_active=True).count()
        total_categories = Category.objects.count()
        active_categories = Category.objects.filter(is_active=True).count()
        
        print(f"\n📊 Database Stats:")
        print(f"   Total Products: {total_products}")
        print(f"   Active Products: {active_products}")
        print(f"   Total Categories: {total_categories}")
        print(f"   Active Categories: {active_categories}")
        
        if total_categories > 0:
            print(f"\n📁 Categories:")
            for category in Category.objects.all()[:10]:
                product_count = Product.objects.filter(category=category).count()
                print(f"   - {category.name}: {product_count} products (Active: {category.is_active})")
        
        if total_products > 0:
            print(f"\n🛍️ Sample Products:")
            for product in Product.objects.all()[:10]:
                print(f"   - {product.name} ({product.item_code})")
                print(f"     Category: {product.category.name if product.category else 'None'}")
                print(f"     In Stock: {product.in_stock}, Active: {product.is_active}")
        else:
            print(f"\n⚠️ NO PRODUCTS FOUND IN DATABASE!")
            print(f"   You need to load products into the database.")
            print(f"   Check if you have a data import script or management command.")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    check_products()
