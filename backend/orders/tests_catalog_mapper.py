"""
Tests for catalog mapper functionality
"""
from django.test import TestCase
from orders.catalog_mapper import CatalogMapper
import os
from pathlib import Path


class CatalogMapperTests(TestCase):
    """Test cases for CatalogMapper"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.mapper = CatalogMapper()
    
    def test_load_catalog(self):
        """Test that catalog loads successfully"""
        catalog = self.mapper.load_catalog()
        
        self.assertIsNotNone(catalog)
        self.assertIn('items', catalog)
        self.assertIn('metadata', catalog)
        self.assertGreater(len(catalog['items']), 0)
    
    def test_find_catalog_item_by_code(self):
        """Test finding item by item code"""
        # Test with a known item code
        item = self.mapper.find_catalog_item('10026')
        
        self.assertIsNotNone(item)
        self.assertEqual(item['item_code'], '10026')
        self.assertIn('item_name', item)
    
    def test_find_catalog_item_by_name(self):
        """Test finding item by item name"""
        # Test with a known item name
        item = self.mapper.find_catalog_item('BLACK CARDAMOM PP')
        
        self.assertIsNotNone(item)
        self.assertEqual(item['item_name'], 'BLACK CARDAMOM PP')
    
    def test_find_catalog_item_not_found(self):
        """Test that non-existent item returns None"""
        item = self.mapper.find_catalog_item('NONEXISTENT_ITEM_12345')
        
        self.assertIsNone(item)
    
    def test_map_order_items_success(self):
        """Test successful mapping of order items"""
        order_items = [
            {'identifier': '10026', 'quantity': 5},
            {'identifier': 'SESAME SEED BLACK PP', 'quantity': 10},
        ]
        
        mapped_items, errors = self.mapper.map_order_items(order_items)
        
        self.assertEqual(len(mapped_items), 2)
        self.assertEqual(len(errors), 0)
        
        # Check first item
        self.assertEqual(mapped_items[0]['item_code'], '10026')
        self.assertEqual(mapped_items[0]['quantity'], 5)
        
        # Check second item
        self.assertEqual(mapped_items[1]['item_code'], '10035')
        self.assertEqual(mapped_items[1]['quantity'], 10)
    
    def test_map_order_items_with_errors(self):
        """Test mapping with some invalid items"""
        order_items = [
            {'identifier': '10026', 'quantity': 5},
            {'identifier': 'INVALID_ITEM', 'quantity': 10},
            {'identifier': '', 'quantity': 5},  # Empty identifier
        ]
        
        mapped_items, errors = self.mapper.map_order_items(order_items)
        
        self.assertEqual(len(mapped_items), 1)  # Only first item should succeed
        self.assertEqual(len(errors), 2)  # Two errors expected
        
        # Check that error messages are informative
        self.assertTrue(any('INVALID_ITEM' in error for error in errors))
        self.assertTrue(any('Missing' in error for error in errors))
    
    def test_generate_csv_from_order(self):
        """Test CSV generation from order items"""
        order_items = [
            {'identifier': '10026', 'quantity': 5},
            {'identifier': '10100', 'quantity': 3},
        ]
        
        csv_content, errors = self.mapper.generate_csv_from_order(order_items)
        
        self.assertEqual(len(errors), 0)
        self.assertIsNotNone(csv_content)
        self.assertIn('Item Code', csv_content)
        self.assertIn('Description', csv_content)
        self.assertIn('Quantity', csv_content)
        self.assertIn('10026', csv_content)
        self.assertIn('10100', csv_content)
    
    def test_generate_csv_with_category(self):
        """Test CSV generation with category column"""
        order_items = [
            {'identifier': '10026', 'quantity': 5},
        ]
        
        csv_content, errors = self.mapper.generate_csv_from_order(order_items, include_category=True)
        
        self.assertEqual(len(errors), 0)
        self.assertIn('Category', csv_content)
    
    def test_parse_order_from_text(self):
        """Test parsing order items from text"""
        order_text = """
        # Sample order
        10026: 5
        10100, 3
        SESAME SEED BLACK PP: 10
        """
        
        order_items = self.mapper.parse_order_from_text(order_text)
        
        self.assertEqual(len(order_items), 3)
        self.assertEqual(order_items[0]['identifier'], '10026')
        self.assertEqual(order_items[0]['quantity'], 5.0)
        self.assertEqual(order_items[1]['identifier'], '10100')
        self.assertEqual(order_items[1]['quantity'], 3.0)
    
    def test_get_catalog_stats(self):
        """Test getting catalog statistics"""
        stats = self.mapper.get_catalog_stats()
        
        self.assertIn('total_items', stats)
        self.assertIn('categories', stats)
        self.assertIn('category_counts', stats)
        
        self.assertGreater(stats['total_items'], 0)
        self.assertIsInstance(stats['categories'], list)
        self.assertIsInstance(stats['category_counts'], dict)


class CatalogMapperIntegrationTests(TestCase):
    """Integration tests for catalog mapper with real data"""
    
    def test_full_workflow(self):
        """Test complete workflow from text to CSV"""
        mapper = CatalogMapper()
        
        # Sample order text
        order_text = """
        10026, 5
        10100: 3
        SESAME SEED BLACK PP: 10
        """
        
        # Parse text
        order_items = mapper.parse_order_from_text(order_text)
        self.assertEqual(len(order_items), 3)
        
        # Generate CSV
        csv_content, errors = mapper.generate_csv_from_order(order_items)
        
        # Verify results
        self.assertEqual(len(errors), 0)
        self.assertIsNotNone(csv_content)
        
        # Check CSV structure
        lines = csv_content.strip().split('\n')
        self.assertEqual(len(lines), 4)  # Header + 3 data rows
        
        # Check header
        self.assertIn('Item Code', lines[0])
        self.assertIn('Description', lines[0])
        self.assertIn('Quantity', lines[0])
