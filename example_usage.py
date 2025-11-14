#!/usr/bin/env python
"""
Example script demonstrating how to use the catalog mapper to generate CSV from customer orders.

This can be run as a standalone script or imported as a module.
"""
import os
import sys
import django

# Setup Django environment
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'desideliver_backend.settings')
django.setup()

from orders.catalog_mapper import CatalogMapper


def example_basic_usage():
    """Example 1: Basic usage - Generate CSV from order items"""
    print("=" * 60)
    print("Example 1: Basic CSV Generation")
    print("=" * 60)
    
    # Initialize mapper
    mapper = CatalogMapper()
    
    # Define order items
    order_items = [
        {'identifier': '10026', 'quantity': 5},
        {'identifier': '10100', 'quantity': 3},
        {'identifier': 'SESAME SEED BLACK PP', 'quantity': 10}
    ]
    
    # Generate CSV
    csv_content, errors = mapper.generate_csv_from_order(order_items)
    
    print(f"\nProcessed {len(order_items)} items")
    print(f"Errors: {len(errors)}")
    
    if csv_content:
        print("\nGenerated CSV:")
        print(csv_content)
    
    if errors:
        print("\nErrors encountered:")
        for error in errors:
            print(f"  - {error}")


def example_from_text():
    """Example 2: Parse order from text and generate CSV"""
    print("\n" + "=" * 60)
    print("Example 2: Parse Order from Text")
    print("=" * 60)
    
    # Sample order text (as you might receive from a customer)
    order_text = """
    # Customer: ABC Store
    # Date: 2024-11-14
    
    10026, 5
    BLACK CARDAMOM PP: 3
    VEGETABLE OIL 32.5L, 2
    COW GHEE 12X8OZ: 4
    """
    
    mapper = CatalogMapper()
    
    # Parse the text
    order_items = mapper.parse_order_from_text(order_text)
    print(f"\nParsed {len(order_items)} items from text")
    
    # Generate CSV with category
    csv_content, errors = mapper.generate_csv_from_order(order_items, include_category=True)
    
    print("\nGenerated CSV with categories:")
    print(csv_content)


def example_catalog_stats():
    """Example 3: Get catalog statistics"""
    print("\n" + "=" * 60)
    print("Example 3: Catalog Statistics")
    print("=" * 60)
    
    mapper = CatalogMapper()
    stats = mapper.get_catalog_stats()
    
    print(f"\nTotal Items: {stats['total_items']}")
    print(f"\nCategories: {len(stats['categories'])}")
    
    print("\nTop 5 categories by item count:")
    sorted_categories = sorted(
        stats['category_counts'].items(),
        key=lambda x: x[1],
        reverse=True
    )
    
    for category, count in sorted_categories[:5]:
        print(f"  {category}: {count} items")


def example_error_handling():
    """Example 4: Error handling for invalid items"""
    print("\n" + "=" * 60)
    print("Example 4: Error Handling")
    print("=" * 60)
    
    mapper = CatalogMapper()
    
    # Order with some invalid items
    order_items = [
        {'identifier': '10026', 'quantity': 5},
        {'identifier': 'INVALID_ITEM', 'quantity': 10},  # Will fail
        {'identifier': '', 'quantity': 5},  # Will fail
        {'identifier': 'VEGETABLE OIL 32.5L', 'quantity': 2},
    ]
    
    csv_content, errors = mapper.generate_csv_from_order(order_items)
    
    print(f"\nProcessed {len(order_items)} items")
    print(f"Successfully mapped: {csv_content.count(chr(10)) - 1} items")
    print(f"Errors: {len(errors)}")
    
    if errors:
        print("\nError details:")
        for error in errors:
            print(f"  - {error}")
    
    print("\nSuccessfully generated CSV:")
    print(csv_content)


def example_find_items():
    """Example 5: Find specific items in catalog"""
    print("\n" + "=" * 60)
    print("Example 5: Find Items in Catalog")
    print("=" * 60)
    
    mapper = CatalogMapper()
    
    # Search by code
    item = mapper.find_catalog_item('10026')
    if item:
        print(f"\nFound by code:")
        print(f"  Code: {item['item_code']}")
        print(f"  Name: {item['item_name']}")
        print(f"  Category: {item['category']}")
    
    # Search by name
    item = mapper.find_catalog_item('VEGETABLE OIL 32.5L')
    if item:
        print(f"\nFound by name:")
        print(f"  Code: {item['item_code']}")
        print(f"  Name: {item['item_name']}")
        print(f"  Category: {item['category']}")
    
    # Search for non-existent item
    item = mapper.find_catalog_item('NONEXISTENT_ITEM')
    if item is None:
        print(f"\nItem 'NONEXISTENT_ITEM' not found (as expected)")


def main():
    """Run all examples"""
    print("\n" + "=" * 60)
    print("CATALOG MAPPER USAGE EXAMPLES")
    print("=" * 60)
    
    try:
        example_basic_usage()
        example_from_text()
        example_catalog_stats()
        example_error_handling()
        example_find_items()
        
        print("\n" + "=" * 60)
        print("All examples completed successfully!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\nError running examples: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
