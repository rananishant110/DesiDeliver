import csv
import json
import os
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.conf import settings
from products.models import Category, Product


class Command(BaseCommand):
    help = 'Import product catalog from CSV and JSON files'

    def add_arguments(self, parser):
        parser.add_argument(
            '--csv-file',
            type=str,
            help='Path to the CSV catalog file',
            default='../docs/catalog/completecatalog.csv'
        )
        parser.add_argument(
            '--json-file',
            type=str,
            help='Path to the JSON catalog file',
            default='../docs/catalog/catalog.json'
        )
        parser.add_argument(
            '--clear-existing',
            action='store_true',
            help='Clear existing products and categories before import'
        )

    def handle(self, *args, **options):
        csv_file = options['csv_file']
        json_file = options['json_file']
        clear_existing = options['clear_existing']

        # Get absolute paths
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        csv_path = os.path.join(base_dir, csv_file)
        json_path = os.path.join(base_dir, json_file)

        self.stdout.write(f"Starting catalog import...")
        self.stdout.write(f"CSV file: {csv_path}")
        self.stdout.write(f"JSON file: {json_path}")

        if clear_existing:
            self.stdout.write("Clearing existing products and categories...")
            Product.objects.all().delete()
            Category.objects.all().delete()
            self.stdout.write("Existing data cleared.")

        # Import categories first
        self.import_categories(json_path)
        
        # Import products
        self.import_products(csv_path)

        self.stdout.write(self.style.SUCCESS('Catalog import completed successfully!'))

    def import_categories(self, json_file_path):
        """Import categories from JSON file"""
        try:
            with open(json_file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
                
            categories_data = data.get('metadata', {}).get('categories', [])
            
            for category_name in categories_data:
                # Clean category name
                clean_name = category_name.strip()
                if clean_name:
                    # Create slug from name
                    slug = clean_name.lower().replace(' ', '-').replace('&', 'and')
                    
                    category, created = Category.objects.get_or_create(
                        name=clean_name,
                        defaults={
                            'slug': slug,
                            'description': f'Products in the {clean_name} category',
                            'is_active': True
                        }
                    )
                    
                    if created:
                        self.stdout.write(f"Created category: {clean_name}")
                    else:
                        self.stdout.write(f"Category already exists: {clean_name}")
                        
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error importing categories: {str(e)}"))

    def import_products(self, csv_file_path):
        """Import products from CSV file"""
        try:
            with open(csv_file_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                
                products_created = 0
                products_updated = 0
                products_skipped = 0
                
                for row in reader:
                    try:
                        # Skip rows without essential data
                        if not row.get('item_number') or not row.get('item_description'):
                            products_skipped += 1
                            continue
                            
                        item_code = row['item_number'].strip()
                        item_name = row['item_description'].strip()
                        category_name = row.get('product_category', '').strip()
                        
                        # Skip if no category
                        if not category_name:
                            products_skipped += 1
                            continue
                        
                        # Get or create category
                        try:
                            category = Category.objects.get(name=category_name)
                        except Category.DoesNotExist:
                            # Create category if it doesn't exist
                            slug = category_name.lower().replace(' ', '-').replace('&', 'and')
                            category = Category.objects.create(
                                name=category_name,
                                slug=slug,
                                description=f'Products in the {category_name} category',
                                is_active=True
                            )
                            self.stdout.write(f"Created new category: {category_name}")
                        
                        # Parse stock information
                        stock_quantity = self.parse_stock(row.get('stock', '0'))
                        has_stock_info = row.get('has_stock_info', 'FALSE').upper() == 'TRUE'
                        
                        # Determine unit from item description
                        unit = self.determine_unit(item_name)
                        
                        # Create or update product
                        product, created = Product.objects.get_or_create(
                            item_code=item_code,
                            defaults={
                                'name': item_name,
                                'description': f'{item_name} - {category_name} category',
                                'category': category,

                                'unit': unit,
                                'min_order_quantity': Decimal('1.0'),
                                'in_stock': has_stock_info and stock_quantity > 0,
                                'stock_quantity': stock_quantity if has_stock_info else Decimal('0.0'),
                                'brand': self.extract_brand(item_name),
                                'origin': 'India',  # Default origin
                                'is_active': True
                            }
                        )
                        
                        if created:
                            products_created += 1
                        else:
                            # Update existing product
                            product.name = item_name
                            product.description = f'{item_name} - {category_name} category'
                            product.category = category
                            product.unit = unit
                            product.in_stock = has_stock_info and stock_quantity > 0
                            product.stock_quantity = stock_quantity if has_stock_info else product.stock_quantity
                            product.save()
                            products_updated += 1
                            
                    except Exception as e:
                        self.stdout.write(self.style.WARNING(f"Error processing row {row}: {str(e)}"))
                        products_skipped += 1
                        continue
                
                self.stdout.write(f"Products created: {products_created}")
                self.stdout.write(f"Products updated: {products_updated}")
                self.stdout.write(f"Products skipped: {products_skipped}")
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error importing products: {str(e)}"))

    def parse_stock(self, stock_str):
        """Parse stock string to Decimal"""
        try:
            if stock_str and stock_str.strip():
                return Decimal(stock_str)
            return Decimal('0.0')
        except:
            return Decimal('0.0')

    def determine_unit(self, item_name):
        """Determine unit from item name"""
        item_lower = item_name.lower()
        
        if any(word in item_lower for word in ['lb', 'pound']):
            return 'lb'
        elif any(word in item_lower for word in ['kg', 'kilo']):
            return 'kg'
        elif any(word in item_lower for word in ['g', 'gram']):
            return 'g'
        elif any(word in item_lower for word in ['ml', 'liter', 'l']):
            return 'ml'
        elif any(word in item_lower for word in ['oz', 'ounce']):
            return 'oz'
        elif any(word in item_lower for word in ['pack', 'pkg']):
            return 'pack'
        elif any(word in item_lower for word in ['piece', 'pc']):
            return 'piece'
        elif any(word in item_lower for word in ['box', 'case']):
            return 'box'
        else:
            return 'unit'

    def extract_brand(self, item_name):
        """Extract brand name from item name if present"""
        # Common brand indicators
        brand_indicators = ['GM', 'QBV', 'LG', 'LIJJAT', 'HAPPY PANDA', 'MOTHER\'S PRIDE']
        
        for brand in brand_indicators:
            if brand in item_name:
                return brand
        
        return ''
