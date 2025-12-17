"""
Celery tasks for orders app.

This module contains async tasks for order processing, email notifications, and CSV generation.
"""
from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def send_order_confirmation_email(self, order_id, customer_email):
    """
    Send order confirmation email asynchronously.
    
    Args:
        order_id: ID of the order
        customer_email: Customer's email address
    
    Returns:
        bool: True if email sent successfully
    """
    try:
        from orders.models import Order
        
        order = Order.objects.get(id=order_id)
        
        subject = f'Order Confirmation - Order #{order.order_number}'
        message = f'''
        Dear {order.user.get_full_name()},
        
        Thank you for your order!
        
        Order Number: {order.order_number}
        Order Date: {order.created_at.strftime('%B %d, %Y')}
        Total Items: {order.items.count()}
        
        Your order has been received and is being processed.
        
        Best regards,
        DesiDeliver Team
        '''
        
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[customer_email],
            fail_silently=False,
        )
        
        logger.info(f"Order confirmation email sent successfully for order {order_id}")
        return True
        
    except Exception as exc:
        logger.error(f"Failed to send order confirmation email for order {order_id}: {exc}")
        # Retry with exponential backoff
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))


@shared_task(bind=True, max_retries=3)
def send_delivery_notification_email(self, order_id):
    """
    Send delivery notification email to coordinator.
    
    Args:
        order_id: ID of the order
    
    Returns:
        bool: True if email sent successfully
    """
    try:
        from orders.models import Order
        
        order = Order.objects.get(id=order_id)
        
        subject = f'New Order Ready for Delivery - Order #{order.order_number}'
        message = f'''
        New order ready for delivery:
        
        Order Number: {order.order_number}
        Customer: {order.user.get_full_name()}
        Items Count: {order.items.count()}
        Order Date: {order.created_at.strftime('%B %d, %Y %H:%M')}
        
        Please check the admin panel for details.
        '''
        
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.DELIVERY_COORDINATOR_EMAIL],
            fail_silently=False,
        )
        
        logger.info(f"Delivery notification sent for order {order_id}")
        return True
        
    except Exception as exc:
        logger.error(f"Failed to send delivery notification for order {order_id}: {exc}")
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))


@shared_task
def generate_order_csv_async(order_id):
    """
    Generate CSV file for an order asynchronously.
    
    Args:
        order_id: ID of the order
    
    Returns:
        str: Path to generated CSV file
    """
    try:
        from orders.models import Order
        from orders.utils import generate_order_csv
        
        order = Order.objects.get(id=order_id)
        csv_path = generate_order_csv(order)
        
        logger.info(f"CSV generated successfully for order {order_id}: {csv_path}")
        return csv_path
        
    except Exception as exc:
        logger.error(f"Failed to generate CSV for order {order_id}: {exc}")
        raise


@shared_task
def cleanup_old_csv_files():
    """
    Periodic task to clean up old CSV files (older than 7 days).
    
    This should be scheduled with Celery Beat.
    """
    import os
    from datetime import datetime, timedelta
    from pathlib import Path
    
    try:
        csv_dir = Path(settings.MEDIA_ROOT) / 'order_csvs'
        if not csv_dir.exists():
            return
        
        cutoff_date = datetime.now() - timedelta(days=7)
        deleted_count = 0
        
        for csv_file in csv_dir.glob('*.csv'):
            file_mtime = datetime.fromtimestamp(csv_file.stat().st_mtime)
            if file_mtime < cutoff_date:
                csv_file.unlink()
                deleted_count += 1
        
        logger.info(f"Cleaned up {deleted_count} old CSV files")
        return deleted_count
        
    except Exception as exc:
        logger.error(f"Failed to cleanup old CSV files: {exc}")
        raise
