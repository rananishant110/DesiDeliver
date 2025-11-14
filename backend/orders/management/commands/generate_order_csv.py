"""
Django management command to generate CSV files from customer orders using catalog.
"""
from django.core.management.base import BaseCommand, CommandError
from orders.catalog_mapper import CatalogMapper
import sys
import os


class Command(BaseCommand):
    help = 'Generate CSV file from customer order using catalog as source of truth'

    def add_arguments(self, parser):
        parser.add_argument(
            '--input',
            '-i',
            type=str,
            help='Input file containing order items (one per line: "item_code: quantity" or "item_name, quantity")'
        )
        parser.add_argument(
            '--output',
            '-o',
            type=str,
            help='Output CSV file path (default: order_output.csv)'
        )
        parser.add_argument(
            '--catalog',
            '-c',
            type=str,
            help='Path to catalog.json file (default: uses docs/catalog/catalog.json)'
        )
        parser.add_argument(
            '--include-category',
            action='store_true',
            help='Include category column in output CSV'
        )
        parser.add_argument(
            '--interactive',
            action='store_true',
            help='Enter order items interactively'
        )
        parser.add_argument(
            '--stats',
            action='store_true',
            help='Show catalog statistics'
        )

    def handle(self, *args, **options):
        # Initialize catalog mapper
        catalog_path = options.get('catalog')
        mapper = CatalogMapper(catalog_path=catalog_path)
        
        # Show stats if requested
        if options['stats']:
            self.show_catalog_stats(mapper)
            return
        
        # Get order items
        if options['interactive']:
            order_items = self.get_interactive_order()
        elif options['input']:
            order_items = self.read_order_from_file(options['input'], mapper)
        else:
            raise CommandError('Please provide --input <file> or use --interactive mode')
        
        if not order_items:
            raise CommandError('No order items to process')
        
        # Generate CSV
        self.stdout.write(f"Processing {len(order_items)} order items...")
        
        include_category = options.get('include_category', False)
        csv_content, errors = mapper.generate_csv_from_order(order_items, include_category)
        
        # Report errors
        if errors:
            self.stdout.write(self.style.WARNING(f"\nFound {len(errors)} error(s):"))
            for error in errors:
                self.stdout.write(self.style.ERROR(f"  - {error}"))
        
        if not csv_content:
            raise CommandError('No valid items could be mapped to catalog')
        
        # Write output
        output_file = options.get('output', 'order_output.csv')
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(csv_content)
        
        self.stdout.write(
            self.style.SUCCESS(f"\nSuccessfully generated CSV: {output_file}")
        )
        
        # Count successful items
        csv_lines = csv_content.strip().split('\n')
        data_rows = len(csv_lines) - 1  # Subtract header row
        self.stdout.write(f"Total items in CSV: {data_rows}")
    
    def read_order_from_file(self, filepath, mapper):
        """Read order items from a file"""
        if not os.path.exists(filepath):
            raise CommandError(f'Input file not found: {filepath}')
        
        with open(filepath, 'r', encoding='utf-8') as f:
            order_text = f.read()
        
        order_items = mapper.parse_order_from_text(order_text)
        
        if not order_items:
            raise CommandError('No valid order items found in input file')
        
        return order_items
    
    def get_interactive_order(self):
        """Get order items interactively from user input"""
        self.stdout.write(self.style.WARNING(
            "\nInteractive Order Entry"
        ))
        self.stdout.write(
            "Enter order items in format: 'item_code: quantity' or 'item_name, quantity'"
        )
        self.stdout.write("Enter a blank line when done.\n")
        
        order_items = []
        line_num = 1
        
        while True:
            try:
                line = input(f"Item {line_num}: ").strip()
                
                if not line:
                    break
                
                # Parse the line
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
                        line_num += 1
                    except ValueError:
                        self.stdout.write(self.style.ERROR(
                            f"Invalid quantity: {quantity_str}. Please try again."
                        ))
                else:
                    self.stdout.write(self.style.ERROR(
                        "Invalid format. Use 'item_code: quantity' or 'item_name, quantity'"
                    ))
            
            except KeyboardInterrupt:
                self.stdout.write("\n\nOrder entry cancelled.")
                sys.exit(0)
        
        return order_items
    
    def show_catalog_stats(self, mapper):
        """Display catalog statistics"""
        stats = mapper.get_catalog_stats()
        
        self.stdout.write(self.style.SUCCESS("\n=== Catalog Statistics ===\n"))
        self.stdout.write(f"Total Items: {stats['total_items']}")
        self.stdout.write(f"\nCategories ({len(stats['categories'])}):")
        
        for category, count in sorted(
            stats['category_counts'].items(),
            key=lambda x: x[1],
            reverse=True
        ):
            self.stdout.write(f"  - {category}: {count} items")
        
        metadata = stats.get('metadata', {})
        if metadata:
            self.stdout.write(f"\nCatalog Version: {metadata.get('version', 'N/A')}")
            self.stdout.write(f"Generated At: {metadata.get('generated_at', 'N/A')}")
