import os
from typing import Optional
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Content
from .models import Ticket, TicketComment


class TicketEmailService:
    """Service class for sending ticket-related emails"""
    
    def __init__(self):
        self.sendgrid_api_key = getattr(settings, 'SENDGRID_API_KEY', None)
        self.from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@desideliver.com')
        self.support_email = getattr(settings, 'SUPPORT_EMAIL', 'support@desideliver.com')
        
        if self.sendgrid_api_key:
            self.sendgrid_client = SendGridAPIClient(api_key=self.sendgrid_api_key)
        else:
            self.sendgrid_client = None
    
    def send_ticket_created_email(self, ticket: Ticket) -> bool:
        """
        Send ticket creation confirmation to customer
        
        Args:
            ticket: Ticket instance
            
        Returns:
            bool: True if email sent successfully, False otherwise
        """
        try:
            subject = f"Support Ticket Created - {ticket.ticket_number}"
            customer_email = ticket.customer.email
            
            # Generate HTML content
            html_content = render_to_string(
                'tickets/emails/ticket_created.html',
                {
                    'ticket': ticket,
                    'customer_name': ticket.customer.get_full_name() or ticket.customer.username,
                }
            )
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
            print(f"Error sending ticket created email: {str(e)}")
            return False
    
    def send_comment_added_email(self, ticket: Ticket, comment: TicketComment) -> bool:
        """
        Send notification when a comment is added to a ticket
        
        Args:
            ticket: Ticket instance
            comment: TicketComment instance
            
        Returns:
            bool: True if email sent successfully, False otherwise
        """
        try:
            # If staff added comment, notify customer
            # If customer added comment, notify support team
            if comment.is_staff_comment:
                subject = f"New Response on Ticket {ticket.ticket_number}"
                to_email = ticket.customer.email
                recipient_name = ticket.customer.get_full_name() or ticket.customer.username
            else:
                subject = f"Customer Reply on Ticket {ticket.ticket_number}"
                to_email = self.support_email
                recipient_name = "Support Team"
            
            # Generate HTML content
            html_content = render_to_string(
                'tickets/emails/comment_added.html',
                {
                    'ticket': ticket,
                    'comment': comment,
                    'recipient_name': recipient_name,
                    'author_name': comment.author.get_full_name() or comment.author.username,
                }
            )
            text_content = strip_tags(html_content)
            
            if self.sendgrid_client:
                return self._send_sendgrid_email(
                    to_email=to_email,
                    subject=subject,
                    html_content=html_content,
                    text_content=text_content
                )
            else:
                return self._send_django_email(
                    to_email=to_email,
                    subject=subject,
                    html_content=html_content,
                    text_content=text_content
                )
        except Exception as e:
            print(f"Error sending comment added email: {str(e)}")
            return False
    
    def send_status_updated_email(self, ticket: Ticket, old_status: str, new_status: str) -> bool:
        """
        Send notification when ticket status is updated
        
        Args:
            ticket: Ticket instance
            old_status: Previous status
            new_status: New status
            
        Returns:
            bool: True if email sent successfully, False otherwise
        """
        try:
            subject = f"Ticket Status Updated - {ticket.ticket_number}"
            customer_email = ticket.customer.email
            
            # Get human-readable status names
            status_dict = dict(Ticket.STATUS_CHOICES)
            old_status_display = status_dict.get(old_status, old_status)
            new_status_display = status_dict.get(new_status, new_status)
            
            # Generate HTML content
            html_content = render_to_string(
                'tickets/emails/status_updated.html',
                {
                    'ticket': ticket,
                    'customer_name': ticket.customer.get_full_name() or ticket.customer.username,
                    'old_status': old_status_display,
                    'new_status': new_status_display,
                }
            )
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
            print(f"Error sending status updated email: {str(e)}")
            return False
    
    def send_ticket_resolved_email(self, ticket: Ticket) -> bool:
        """
        Send notification when ticket is resolved
        
        Args:
            ticket: Ticket instance
            
        Returns:
            bool: True if email sent successfully, False otherwise
        """
        try:
            subject = f"Ticket Resolved - {ticket.ticket_number}"
            customer_email = ticket.customer.email
            
            # Generate HTML content
            html_content = render_to_string(
                'tickets/emails/ticket_resolved.html',
                {
                    'ticket': ticket,
                    'customer_name': ticket.customer.get_full_name() or ticket.customer.username,
                }
            )
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
            print(f"Error sending ticket resolved email: {str(e)}")
            return False
    
    def send_ticket_closed_email(self, ticket: Ticket) -> bool:
        """
        Send notification when ticket is closed
        
        Args:
            ticket: Ticket instance
            
        Returns:
            bool: True if email sent successfully, False otherwise
        """
        try:
            subject = f"Ticket Closed - {ticket.ticket_number}"
            customer_email = ticket.customer.email
            
            # Generate HTML content
            html_content = render_to_string(
                'tickets/emails/ticket_closed.html',
                {
                    'ticket': ticket,
                    'customer_name': ticket.customer.get_full_name() or ticket.customer.username,
                }
            )
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
            print(f"Error sending ticket closed email: {str(e)}")
            return False
    
    def _send_sendgrid_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: str
    ) -> bool:
        """Send email using SendGrid API"""
        try:
            message = Mail(
                from_email=self.from_email,
                to_emails=to_email,
                subject=subject,
                html_content=Content("text/html", html_content)
            )
            
            response = self.sendgrid_client.send(message)
            return response.status_code in [200, 201, 202]
        except Exception as e:
            print(f"SendGrid error: {str(e)}")
            return False
    
    def _send_django_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: str
    ) -> bool:
        """Send email using Django's email backend"""
        try:
            send_mail(
                subject=subject,
                message=text_content,
                from_email=self.from_email,
                recipient_list=[to_email],
                html_message=html_content,
                fail_silently=False,
            )
            return True
        except Exception as e:
            print(f"Django email error: {str(e)}")
            return False
