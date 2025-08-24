import os
import base64
from io import StringIO
from typing import List, Optional
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import (
    Mail, Attachment, FileContent, FileName, 
    FileType, Disposition, Content
)
from .models import Order
from .utils import CSVGenerator

class EmailService:
    """Service class for sending order-related emails"""
    
    def __init__(self):
        self.sendgrid_api_key = getattr(settings, 'SENDGRID_API_KEY', None)
        self.from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@desideliver.com')
        self.delivery_coordinator_email = getattr(settings, 'DELIVERY_COORDINATOR_EMAIL', 'delivery@desideliver.com')
        
        if self.sendgrid_api_key:
            self.sendgrid_client = SendGridAPIClient(api_key=self.sendgrid_api_key)
        else:
            self.sendgrid_client = None
    
    def send_order_confirmation_email(self, order: Order, customer_email: str) -> bool:
        """
        Send order confirmation email to customer
        
        Args:
            order: Order instance
            customer_email: Customer's email address
            
        Returns:
            bool: True if email sent successfully, False otherwise
        """
        try:
            subject = f"Order Confirmation - {order.order_number}"
            
            # Generate HTML content
            html_content = self._generate_order_confirmation_html(order)
            text_content = strip_tags(html_content)
            
            if self.sendgrid_client:
                return self._send_sendgrid_email(
                    to_email=customer_email,
                    subject=subject,
                    html_content=html_content,
                    text_content=text_content
                )
            else:
                return self._send_django_email(
                    to_email=customer_email,
                    subject=subject,
                    html_content=html_content,
                    text_content=text_content
                )
                
        except Exception as e:
            print(f"Failed to send order confirmation email: {str(e)}")
            return False
    
    def send_delivery_coordinator_notification(self, order: Order) -> bool:
        """
        Send order notification to delivery coordinator with CSV attachment
        
        Args:
            order: Order instance
            
        Returns:
            bool: True if email sent successfully, False otherwise
        """
        try:
            subject = f"New Order Received - {order.order_number}"
            
            # Generate HTML content
            html_content = self._generate_delivery_notification_html(order)
            text_content = strip_tags(html_content)
            
            # Generate CSV attachment
            csv_content = CSVGenerator.generate_order_csv(order)
            csv_filename = CSVGenerator.generate_order_csv_filename(order)
            
            if self.sendgrid_client:
                return self._send_sendgrid_email_with_attachment(
                    to_email=self.delivery_coordinator_email,
                    subject=subject,
                    html_content=html_content,
                    text_content=text_content,
                    attachment_content=csv_content,
                    attachment_filename=csv_filename
                )
            else:
                return self._send_django_email_with_attachment(
                    to_email=self.delivery_coordinator_email,
                    subject=subject,
                    html_content=html_content,
                    text_content=text_content,
                    attachment_content=csv_content,
                    attachment_filename=csv_filename
                )
                
        except Exception as e:
            print(f"Failed to send delivery coordinator notification: {str(e)}")
            return False
    
    def send_daily_orders_summary(self, orders: List[Order], date_str: str) -> bool:
        """
        Send daily orders summary to delivery coordinator
        
        Args:
            orders: List of orders for the day
            date_str: Date string for the summary
            
        Returns:
            bool: True if email sent successfully, False otherwise
        """
        try:
            subject = f"Daily Orders Summary - {date_str}"
            
            # Generate HTML content
            html_content = self._generate_daily_summary_html(orders, date_str)
            text_content = strip_tags(html_content)
            
            # Generate CSV attachment
            csv_content = CSVGenerator.generate_daily_orders_csv(orders, orders[0].created_at.date())
            csv_filename = CSVGenerator.generate_daily_orders_filename(orders[0].created_at.date())
            
            if self.sendgrid_client:
                return self._send_sendgrid_email_with_attachment(
                    to_email=self.delivery_coordinator_email,
                    subject=subject,
                    html_content=html_content,
                    text_content=text_content,
                    attachment_content=csv_content,
                    attachment_filename=csv_filename
                )
            else:
                return self._send_django_email_with_attachment(
                    to_email=self.delivery_coordinator_email,
                    subject=subject,
                    html_content=html_content,
                    text_content=text_content,
                    attachment_content=csv_content,
                    attachment_filename=csv_filename
                )
                
        except Exception as e:
            print(f"Failed to send daily orders summary: {str(e)}")
            return False
    
    def _send_sendgrid_email(self, to_email: str, subject: str, 
                           html_content: str, text_content: str) -> bool:
        """Send email using SendGrid"""
        try:
            message = Mail(
                from_email=self.from_email,
                to_emails=to_email,
                subject=subject,
                html_content=html_content
            )
            
            # Add text content as alternative
            message.add_content(Content("text/plain", text_content))
            
            response = self.sendgrid_client.send(message)
            return response.status_code in [200, 201, 202]
            
        except Exception as e:
            print(f"SendGrid email failed: {str(e)}")
            return False
    
    def _send_sendgrid_email_with_attachment(self, to_email: str, subject: str,
                                           html_content: str, text_content: str,
                                           attachment_content: str, 
                                           attachment_filename: str) -> bool:
        """Send email with attachment using SendGrid"""
        try:
            message = Mail(
                from_email=self.from_email,
                to_emails=to_email,
                subject=subject,
                html_content=html_content
            )
            
            # Add text content as alternative
            message.add_content(Content("text/plain", text_content))
            
            # Add CSV attachment
            encoded_file = base64.b64encode(attachment_content.encode('utf-8')).decode()
            attached_file = Attachment(
                FileContent(encoded_file),
                FileName(attachment_filename),
                FileType('text/csv'),
                Disposition('attachment')
            )
            message.attachment = attached_file
            
            response = self.sendgrid_client.send(message)
            return response.status_code in [200, 201, 202]
            
        except Exception as e:
            print(f"SendGrid email with attachment failed: {str(e)}")
            return False
    
    def _send_django_email(self, to_email: str, subject: str,
                          html_content: str, text_content: str) -> bool:
        """Send email using Django's built-in email backend"""
        try:
            send_mail(
                subject=subject,
                message=text_content,
                from_email=self.from_email,
                recipient_list=[to_email],
                html_message=html_content,
                fail_silently=False
            )
            return True
            
        except Exception as e:
            print(f"Django email failed: {str(e)}")
            return False
    
    def _send_django_email_with_attachment(self, to_email: str, subject: str,
                                         html_content: str, text_content: str,
                                         attachment_content: str, 
                                         attachment_filename: str) -> bool:
        """Send email with attachment using Django's email backend"""
        try:
            from django.core.mail import EmailMessage
            
            email = EmailMessage(
                subject=subject,
                body=html_content,
                from_email=self.from_email,
                to=[to_email]
            )
            email.content_subtype = "html"
            
            # Add CSV attachment
            email.attach(attachment_filename, attachment_content, 'text/csv')
            
            email.send()
            return True
            
        except Exception as e:
            print(f"Django email with attachment failed: {str(e)}")
            return False
    
    def _generate_order_confirmation_html(self, order: Order) -> str:
        """Generate HTML content for order confirmation email"""
        context = {
            'order': order,
            'order_date': order.created_at.strftime('%B %d, %Y at %I:%M %p'),
            'total_items': order.total_items,
            'business_name': order.business_name,
            'delivery_address': order.delivery_address
        }
        
        return render_to_string('orders/emails/order_confirmation.html', context)
    
    def _generate_delivery_notification_html(self, order: Order) -> str:
        """Generate HTML content for delivery coordinator notification"""
        context = {
            'order': order,
            'order_date': order.created_at.strftime('%B %d, %Y at %I:%M %p'),
            'total_items': order.total_items,
            'business_name': order.business_name,
            'contact_person': order.contact_person,
            'phone_number': order.phone_number,
            'delivery_address': order.delivery_address
        }
        
        return render_to_string('orders/emails/delivery_notification.html', context)
    
    def _generate_daily_summary_html(self, orders: List[Order], date_str: str) -> str:
        """Generate HTML content for daily orders summary"""
        context = {
            'orders': orders,
            'date_str': date_str,
            'total_orders': len(orders),
            'total_items': sum(order.total_items for order in orders)
        }
        
        return render_to_string('orders/emails/daily_summary.html', context)
