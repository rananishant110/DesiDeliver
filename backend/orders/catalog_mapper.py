"""
Catalog mapper for generating CSV files from customer orders using catalog.json as source of truth.
"""
import csv
import io
import json
import os
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple


class CatalogMapper:
    """Maps customer orders to catalog items and generates CSV files"""
    
    def __init__(self, catalog_path: Optional[str] = None):
        """
        Initialize the catalog mapper
        
        Args:
            catalog_path: Optional path to catalog.json. If not provided, uses default location.
        """
        if catalog_path is None:
            # Default to the catalog.json in the docs/catalog directory
            # Go up from backend/orders/catalog_mapper.py to project root
            base_dir = Path(__file__).resolve().parent.parent.parent
            catalog_path = base_dir / 'docs' / 'catalog' / 'catalog.json'
        
        self.catalog_path = Path(catalog_path)
        self._catalog_data = None
        self._catalog_index = None
        
    def load_catalog(self) -> Dict[str, Any]:
        """
        Load catalog data from JSON file
        
        Returns:
            Dict containing catalog data
            
        Raises:
            FileNotFoundError: If catalog file doesn't exist
            json.JSONDecodeError: If catalog file is not valid JSON
        """
        if self._catalog_data is None:
            if not self.catalog_path.exists():
                raise FileNotFoundError(f"Catalog file not found at: {self.catalog_path}")
            
            with open(self.catalog_path, 'r', encoding='utf-8') as f:
                self._catalog_data = json.load(f)
            
            # Build index for faster lookups
            self._build_catalog_index()
        
        return self._catalog_data
    
    def _build_catalog_index(self):
        """Build an index for quick item lookups by item_code and item_name"""
        self._catalog_index = {
            'by_code': {},
            'by_name': {},
            'by_name_lower': {}
        }
        
        items = self._catalog_data.get('items', [])
        for item in items:
            item_code = item.get('item_code', '').strip()
            item_name = item.get('item_name', '').strip()
            
            if item_code:
                self._catalog_index['by_code'][item_code] = item
            
            if item_name:
                self._catalog_index['by_name'][item_name] = item
                self._catalog_index['by_name_lower'][item_name.lower()] = item
    
    def find_catalog_item(self, identifier: str) -> Optional[Dict[str, Any]]:
        """
        Find an item in the catalog by item code or name
        
        Args:
            identifier: Item code or item name to search for
            
        Returns:
            Dict containing item data if found, None otherwise
        """
        if self._catalog_index is None:
            self.load_catalog()
        
        identifier = identifier.strip()
        
        # Try exact match by code first
        if identifier in self._catalog_index['by_code']:
            return self._catalog_index['by_code'][identifier]
        
        # Try exact match by name
        if identifier in self._catalog_index['by_name']:
            return self._catalog_index['by_name'][identifier]
        
        # Try case-insensitive match by name
        if identifier.lower() in self._catalog_index['by_name_lower']:
            return self._catalog_index['by_name_lower'][identifier.lower()]
        
        return None
    
    def map_order_items(self, order_items: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], List[str]]:
        """
        Map customer order items to catalog items
        
        Args:
            order_items: List of dicts with 'identifier' (item code or name) and 'quantity' keys
            
        Returns:
            Tuple of (mapped_items, errors)
            - mapped_items: List of successfully mapped items
            - errors: List of error messages for items that couldn't be mapped
        """
        self.load_catalog()
        
        mapped_items = []
        errors = []
        
        for idx, item in enumerate(order_items, start=1):
            identifier = item.get('identifier', '').strip()
            quantity = item.get('quantity', 0)
            
            if not identifier:
                errors.append(f"Row {idx}: Missing item identifier")
                continue
            
            if not quantity or quantity <= 0:
                errors.append(f"Row {idx}: Invalid quantity for '{identifier}'")
                continue
            
            catalog_item = self.find_catalog_item(identifier)
            
            if catalog_item is None:
                errors.append(f"Row {idx}: Item '{identifier}' not found in catalog")
                continue
            
            mapped_items.append({
                'item_code': catalog_item.get('item_code', ''),
                'description': catalog_item.get('item_name', ''),
                'quantity': quantity,
                'category': catalog_item.get('category', ''),
                'source_file': catalog_item.get('source_file', ''),
            })
        
        return mapped_items, errors
    
    def generate_csv_from_order(
        self, 
        order_items: List[Dict[str, Any]], 
        include_category: bool = False
    ) -> Tuple[str, List[str]]:
        """
        Generate CSV content from customer order items
        
        Args:
            order_items: List of dicts with 'identifier' and 'quantity' keys
            include_category: Whether to include category column in CSV
            
        Returns:
            Tuple of (csv_content, errors)
            - csv_content: Generated CSV as string
            - errors: List of error messages
        """
        mapped_items, errors = self.map_order_items(order_items)
        
        if not mapped_items:
            return "", errors
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        if include_category:
            writer.writerow(['Item Code', 'Description', 'Quantity', 'Category'])
        else:
            writer.writerow(['Item Code', 'Description', 'Quantity'])
        
        # Write data rows
        for item in mapped_items:
            if include_category:
                writer.writerow([
                    item['item_code'],
                    item['description'],
                    item['quantity'],
                    item['category']
                ])
            else:
                writer.writerow([
                    item['item_code'],
                    item['description'],
                    item['quantity']
                ])
        
        return output.getvalue(), errors
    
    def parse_order_from_text(self, order_text: str) -> List[Dict[str, Any]]:
        """
        Parse order items from text input
        
        Supports formats:
        - "item_code: quantity" or "item_code, quantity"
        - "item_name: quantity" or "item_name, quantity"
        
        Args:
            order_text: Text containing order items, one per line
            
        Returns:
            List of dicts with 'identifier' and 'quantity' keys
        """
        order_items = []
        
        for line in order_text.strip().split('\n'):
            line = line.strip()
            if not line or line.startswith('#'):  # Skip empty lines and comments
                continue
            
            # Try to parse the line
            # Format: "identifier: quantity" or "identifier, quantity"
            parts = None
            if ':' in line:
                parts = [p.strip() for p in line.split(':', 1)]
            elif ',' in line:
                parts = [p.strip() for p in line.split(',', 1)]
            
            if parts and len(parts) == 2:
                identifier, quantity_str = parts
                try:
                    quantity = float(quantity_str)
                    order_items.append({
                        'identifier': identifier,
                        'quantity': quantity
                    })
                except ValueError:
                    # Skip lines that can't be parsed
                    continue
        
        return order_items
    
    def get_catalog_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the catalog
        
        Returns:
            Dict containing catalog statistics
        """
        self.load_catalog()
        
        metadata = self._catalog_data.get('metadata', {})
        items = self._catalog_data.get('items', [])
        
        # Count items by category
        category_counts = {}
        for item in items:
            category = item.get('category', 'Unknown')
            category_counts[category] = category_counts.get(category, 0) + 1
        
        return {
            'total_items': len(items),
            'categories': list(category_counts.keys()),
            'category_counts': category_counts,
            'metadata': metadata
        }
