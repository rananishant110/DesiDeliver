import csv
import io
from datetime import datetime
from typing import List, Dict, Any, Tuple
from .models import Order, OrderItem
from .catalog_mapper import CatalogMapper

class CSVGenerator:
    """Utility class for generating CSV files from order data"""
    
    @staticmethod
    def generate_order_csv(order: Order) -> str:
        """
        Generate CSV content for a specific order
        
        Args:
            order: Order instance
            
        Returns:
            str: CSV content as string
        """
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow([
            'Item Code',
            'Description', 
            'Quantity',
            'Unit',
            'Category'
        ])
        
        # Write order items
        for item in order.items.all():
            writer.writerow([
                item.product.item_code,
                item.product.name,
                item.quantity,
                item.product.unit,
                item.product.category.name
            ])
        
        return output.getvalue()
    
    @staticmethod
    def generate_order_csv_filename(order: Order) -> str:
        """
        Generate filename for order CSV
        
        Args:
            order: Order instance
            
        Returns:
            str: Filename for the CSV
        """
        order_date = order.created_at.strftime('%Y%m%d')
        return f"DesiDeliver_Order_{order.order_number}_{order_date}.csv"
    
    @staticmethod
    def generate_orders_summary_csv(orders: List[Order]) -> str:
        """
        Generate CSV content for multiple orders summary
        
        Args:
            orders: List of Order instances
            
        Returns:
            str: CSV content as string
        """
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow([
            'Order Number',
            'Business Name',
            'Contact Person',
            'Phone Number',
            'Delivery Address',
            'Order Date',
            'Total Items',
            'Status'
        ])
        
        # Write order summaries
        for order in orders:
            writer.writerow([
                order.order_number,
                order.business_name,
                order.contact_person,
                order.phone_number,
                order.delivery_address,
                order.created_at.strftime('%Y-%m-%d %H:%M'),
                order.total_items,
                order.get_status_display()
            ])
        
        return output.getvalue()
    
    @staticmethod
    def generate_daily_orders_csv(orders: List[Order], date: datetime.date) -> str:
        """
        Generate CSV content for all orders on a specific date
        
        Args:
            orders: List of Order instances for the date
            date: Date for the orders
            
        Returns:
            str: CSV content as string
        """
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow([
            'Order Number',
            'Business Name',
            'Item Code',
            'Description',
            'Quantity',
            'Unit',
            'Category',
            'Delivery Address',
            'Contact Person',
            'Phone Number'
        ])
        
        # Write all items from all orders
        for order in orders:
            for item in order.items.all():
                writer.writerow([
                    order.order_number,
                    order.business_name,
                    item.product.item_code,
                    item.product.name,
                    item.quantity,
                    item.product.unit,
                    item.product.category.name,
                    order.delivery_address,
                    order.contact_person,
                    order.phone_number
                ])
        
        return output.getvalue()
    
    @staticmethod
    def generate_daily_orders_filename(date: datetime.date) -> str:
        """
        Generate filename for daily orders CSV
        
        Args:
            date: Date for the orders
            
        Returns:
            str: Filename for the CSV
        """
        date_str = date.strftime('%Y%m%d')
        return f"DesiDeliver_DailyOrders_{date_str}.csv"
    
    @staticmethod
    def validate_csv_content(csv_content: str) -> Dict[str, Any]:
        """
        Validate CSV content and return validation results
        
        Args:
            csv_content: CSV content as string
            
        Returns:
            Dict with validation results
        """
        try:
            # Parse CSV to check format
            reader = csv.reader(io.StringIO(csv_content))
            rows = list(reader)
            
            if not rows:
                return {
                    'valid': False,
                    'error': 'CSV is empty',
                    'row_count': 0
                }
            
            # Check header
            header = rows[0]
            expected_headers = ['Item Code', 'Description', 'Quantity', 'Unit', 'Category']
            
            if len(header) != len(expected_headers):
                return {
                    'valid': False,
                    'error': f'Expected {len(expected_headers)} columns, got {len(header)}',
                    'row_count': len(rows)
                }
            
            # Check data rows
            data_rows = rows[1:]
            if not data_rows:
                return {
                    'valid': False,
                    'error': 'No data rows found',
                    'row_count': len(rows)
                }
            
            return {
                'valid': True,
                'row_count': len(rows),
                'data_rows': len(data_rows),
                'columns': len(header)
            }
            
        except Exception as e:
            return {
                'valid': False,
                'error': f'CSV parsing error: {str(e)}',
                'row_count': 0
            }


def generate_csv_from_text_order(order_text: str, include_category: bool = False) -> Tuple[str, List[str]]:
    """
    Generate CSV from text-based customer order using catalog
    
    Args:
        order_text: Text containing order items (one per line: "item_code: quantity")
        include_category: Whether to include category in CSV
        
    Returns:
        Tuple of (csv_content, errors)
    """
    mapper = CatalogMapper()
    order_items = mapper.parse_order_from_text(order_text)
    
    if not order_items:
        return "", ["No valid order items found in input text"]
    
    return mapper.generate_csv_from_order(order_items, include_category)
