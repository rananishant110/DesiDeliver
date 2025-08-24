import logging
from typing import Optional, List
from django.db import transaction
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from .models import Order, OrderItem
from .email_service import EmailService
from .utils import CSVGenerator

logger = logging.getLogger(__name__)

class OrderProcessor:
    """Service class for automated order processing and workflow management"""
    
    def __init__(self):
        self.email_service = EmailService()
    
    def process_order_status_change(self, order: Order, new_status: str, old_status: str, 
                                 notes: str = None, user: Optional[str] = None) -> bool:
        """
        Process order status change and send appropriate notifications
        
        Args:
            order: Order instance
            new_status: New status being set
            old_status: Previous status
            notes: Optional notes about the status change
            user: User making the status change (optional)
            
        Returns:
            bool: True if processing successful, False otherwise
        """
        try:
            logger.info(f"Processing status change for order {order.order_number}: {old_status} -> {new_status}")
            
            # Update order status
            order.status = new_status
            order.updated_at = timezone.now()
            order.save()
            
            # Send status-specific notifications
            self._send_status_change_notifications(order, new_status, old_status, notes, user)
            
            # Process status-specific actions
            self._process_status_actions(order, new_status, old_status)
            
            logger.info(f"Successfully processed status change for order {order.order_number}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to process status change for order {order.order_number}: {str(e)}")
            return False
    
    def _send_status_change_notifications(self, order: Order, new_status: str, 
                                        old_status: str, notes: str = None, user: str = None):
        """Send appropriate notifications based on status change"""
        
        # Customer notifications
        if new_status in ['confirmed', 'processing', 'ready', 'delivered']:
            self._send_customer_status_update(order, new_status, notes)
        
        # Coordinator notifications
        if new_status in ['confirmed', 'processing', 'ready']:
            self._send_coordinator_status_update(order, new_status, old_status, notes, user)
        
        # Special notifications
        if new_status == 'ready':
            self._send_delivery_ready_notification(order)
        elif new_status == 'delivered':
            self._send_delivery_completion_notification(order)
        elif new_status == 'cancelled':
            self._send_cancellation_notification(order, notes)
    
    def _send_customer_status_update(self, order: Order, new_status: str, notes: str = None):
        """Send status update email to customer"""
        try:
            subject = f"Order {order.order_number} Status Update - {order.get_status_display()}"
            
            # Generate status-specific email content
            html_content = self._generate_customer_status_email(order, new_status, notes)
            text_content = self._strip_html(html_content)
            
            # Send email
            if self.email_service.sendgrid_client:
                success = self.email_service._send_sendgrid_email(
                    to_email=order.customer.email,
                    subject=subject,
                    html_content=html_content,
                    text_content=text_content
                )
            else:
                success = self.email_service._send_django_email(
                    to_email=order.customer.email,
                    subject=subject,
                    html_content=html_content,
                    text_content=text_content
                )
            
            if success:
                logger.info(f"Customer status update email sent for order {order.order_number}")
            else:
                logger.warning(f"Failed to send customer status update email for order {order.order_number}")
                
        except Exception as e:
            logger.error(f"Error sending customer status update email: {str(e)}")
    
    def _send_coordinator_status_update(self, order: Order, new_status: str, 
                                      old_status: str, notes: str = None, user: str = None):
        """Send status update notification to delivery coordinator"""
        try:
            subject = f"Order {order.order_number} Status Changed - {order.get_status_display()}"
            
            # Generate coordinator notification
            html_content = self._generate_coordinator_status_email(order, new_status, old_status, notes, user)
            text_content = self._strip_html(html_content)
            
            # Send email
            if self.email_service.sendgrid_client:
                success = self.email_service._send_sendgrid_email(
                    to_email=self.email_service.delivery_coordinator_email,
                    subject=subject,
                    html_content=html_content,
                    text_content=text_content
                )
            else:
                success = self.email_service._send_django_email(
                    to_email=self.email_service.delivery_coordinator_email,
                    subject=subject,
                    html_content=html_content,
                    text_content=text_content
                )
            
            if success:
                logger.info(f"Coordinator status update email sent for order {order.order_number}")
            else:
                logger.warning(f"Failed to send coordinator status update email for order {order.order_number}")
                
        except Exception as e:
            logger.error(f"Error sending coordinator status update email: {str(e)}")
    
    def _send_delivery_ready_notification(self, order: Order):
        """Send notification when order is ready for delivery"""
        try:
            subject = f"🚚 Order {order.order_number} Ready for Delivery!"
            
            html_content = self._generate_delivery_ready_email(order)
            text_content = self._strip_html(html_content)
            
            # Send to coordinator
            if self.email_service.sendgrid_client:
                self.email_service._send_sendgrid_email(
                    to_email=self.email_service.delivery_coordinator_email,
                    subject=subject,
                    html_content=html_content,
                    text_content=text_content
                )
            else:
                self.email_service._send_django_email(
                    to_email=self.email_service.delivery_coordinator_email,
                    subject=subject,
                    html_content=html_content,
                    text_content=text_content
                )
            
            # Send to customer
            customer_subject = f"Your Order {order.order_number} is Ready for Delivery!"
            if self.email_service.sendgrid_client:
                self.email_service._send_sendgrid_email(
                    to_email=order.customer.email,
                    subject=customer_subject,
                    html_content=html_content,
                    text_content=text_content
                )
            else:
                self.email_service._send_django_email(
                    to_email=order.customer.email,
                    subject=customer_subject,
                    html_content=html_content,
                    text_content=text_content
                )
                
        except Exception as e:
            logger.error(f"Error sending delivery ready notification: {str(e)}")
    
    def _send_delivery_completion_notification(self, order: Order):
        """Send notification when order is delivered"""
        try:
            subject = f"✅ Order {order.order_number} Delivered Successfully!"
            
            html_content = self._generate_delivery_completion_email(order)
            text_content = self._strip_html(html_content)
            
            # Send to customer
            if self.email_service.sendgrid_client:
                self.email_service._send_sendgrid_email(
                    to_email=order.customer.email,
                    subject=subject,
                    html_content=html_content,
                    text_content=text_content
                )
            else:
                self.email_service._send_django_email(
                    to_email=order.customer.email,
                    subject=subject,
                    html_content=html_content,
                    text_content=text_content
                )
                
        except Exception as e:
            logger.error(f"Error sending delivery completion notification: {str(e)}")
    
    def _send_cancellation_notification(self, order: Order, notes: str = None):
        """Send cancellation notification"""
        try:
            subject = f"❌ Order {order.order_number} Cancelled"
            
            html_content = self._generate_cancellation_email(order, notes)
            text_content = self._strip_html(html_content)
            
            # Send to customer
            if self.email_service.sendgrid_client:
                self.email_service._send_sendgrid_email(
                    to_email=order.customer.email,
                    subject=subject,
                    html_content=html_content,
                    text_content=text_content
                )
            else:
                self.email_service._send_django_email(
                    to_email=order.customer.email,
                    subject=subject,
                    html_content=html_content,
                    text_content=text_content
                )
                
        except Exception as e:
            logger.error(f"Error sending cancellation notification: {str(e)}")
    
    def _process_status_actions(self, order: Order, new_status: str, old_status: str):
        """Process status-specific actions"""
        
        if new_status == 'confirmed':
            # Update inventory or trigger other business logic
            self._process_order_confirmation(order)
        elif new_status == 'processing':
            # Start processing workflow
            self._process_order_processing(order)
        elif new_status == 'ready':
            # Prepare for delivery
            self._process_order_ready(order)
        elif new_status == 'delivered':
            # Complete delivery process
            self._process_order_delivered(order)
    
    def _process_order_confirmation(self, order: Order):
        """Process actions when order is confirmed"""
        # Update inventory, allocate resources, etc.
        logger.info(f"Processing order confirmation for {order.order_number}")
    
    def _process_order_processing(self, order: Order):
        """Process actions when order processing starts"""
        # Start production, packaging, etc.
        logger.info(f"Processing order processing start for {order.order_number}")
    
    def _process_order_ready(self, order: Order):
        """Process actions when order is ready for delivery"""
        # Schedule delivery, notify delivery team, etc.
        logger.info(f"Processing order ready for delivery {order.order_number}")
    
    def _process_order_delivered(self, order: Order):
        """Process actions when order is delivered"""
        # Update delivery records, trigger follow-up, etc.
        order.actual_delivery_date = timezone.now().date()
        order.save()
        logger.info(f"Processing order delivery completion for {order.order_number}")
    
    def _strip_html(self, html_content: str) -> str:
        """Strip HTML tags to create plain text version"""
        try:
            from django.utils.html import strip_tags
            return strip_tags(html_content)
        except ImportError:
            import re
            return re.sub(r'<[^>]+>', '', html_content)
    
    def _generate_customer_status_email(self, order: Order, new_status: str, notes: str = None) -> str:
        """Generate customer status update email content"""
        # This would use a template similar to our existing email templates
        # For now, return a simple HTML structure
        return f"""
        <html>
        <body>
            <h2>Order Status Update</h2>
            <p>Your order {order.order_number} status has been updated to: <strong>{order.get_status_display()}</strong></p>
            {f'<p><strong>Notes:</strong> {notes}</p>' if notes else ''}
            <p>Thank you for choosing DesiDeliver!</p>
        </body>
        </html>
        """
    
    def _generate_coordinator_status_email(self, order: Order, new_status: str, 
                                         old_status: str, notes: str = None, user: str = None) -> str:
        """Generate coordinator status update email content"""
        return f"""
        <html>
        <body>
            <h2>Order Status Change Notification</h2>
            <p>Order {order.order_number} status changed from <strong>{old_status}</strong> to <strong>{new_status}</strong></p>
            {f'<p><strong>Changed by:</strong> {user}</p>' if user else ''}
            {f'<p><strong>Notes:</strong> {notes}</p>' if notes else ''}
            <p>Please take appropriate action.</p>
        </body>
        </html>
        """
    
    def _generate_delivery_ready_email(self, order: Order) -> str:
        """Generate delivery ready email content"""
        return f"""
        <html>
        <body>
            <h2>🚚 Order Ready for Delivery!</h2>
            <p>Order {order.order_number} is now ready for delivery to:</p>
            <p><strong>{order.business_name}</strong><br>
            {order.delivery_address}</p>
            <p>Please arrange delivery as soon as possible.</p>
        </body>
        </html>
        """
    
    def _generate_delivery_completion_email(self, order: Order) -> str:
        """Generate delivery completion email content"""
        return f"""
        <html>
        <body>
            <h2>✅ Order Delivered Successfully!</h2>
            <p>Your order {order.order_number} has been delivered successfully!</p>
            <p>Thank you for choosing DesiDeliver!</p>
        </body>
        </html>
        """
    
    def _generate_cancellation_email(self, order: Order, notes: str = None) -> str:
        """Generate cancellation email content"""
        return f"""
        <html>
        <body>
            <h2>❌ Order Cancelled</h2>
            <p>Your order {order.order_number} has been cancelled.</p>
            {f'<p><strong>Reason:</strong> {notes}</p>' if notes else ''}
            <p>If you have any questions, please contact us.</p>
        </body>
        </html>
        """
