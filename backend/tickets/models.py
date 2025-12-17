from django.db import models
from django.conf import settings
from django.core.validators import MinLengthValidator, MaxLengthValidator
from django.utils import timezone
import datetime

class Ticket(models.Model):
    """
    Customer support ticket model for handling complaints, concerns, and inquiries
    """
    
    # Category choices
    CATEGORY_CHOICES = [
        ('order_issue', 'Order Issue'),
        ('product_quality', 'Product Quality'),
        ('delivery', 'Delivery Problem'),
        ('payment', 'Payment Issue'),
        ('account', 'Account Support'),
        ('general', 'General Inquiry'),
    ]
    
    # Priority choices
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    
    # Status choices
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
    ]
    
    # Core fields
    ticket_number = models.CharField(
        max_length=20,
        unique=True,
        help_text="Auto-generated unique ticket identifier"
    )
    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='tickets',
        help_text="Customer who created the ticket"
    )
    order = models.ForeignKey(
        'orders.Order',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tickets',
        help_text="Related order (optional)"
    )
    
    # Ticket details
    subject = models.CharField(
        max_length=200,
        validators=[MinLengthValidator(5)],
        help_text="Brief ticket subject"
    )
    description = models.TextField(
        validators=[MinLengthValidator(20), MaxLengthValidator(2000)],
        help_text="Detailed description of the issue"
    )
    category = models.CharField(
        max_length=50,
        choices=CATEGORY_CHOICES,
        help_text="Type of issue"
    )
    priority = models.CharField(
        max_length=20,
        choices=PRIORITY_CHOICES,
        default='medium',
        help_text="Priority level"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='open',
        help_text="Current ticket status"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    resolved_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When ticket was marked resolved"
    )
    closed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When ticket was marked closed"
    )
    
    class Meta:
        verbose_name = 'Ticket'
        verbose_name_plural = 'Tickets'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['ticket_number']),
            models.Index(fields=['customer']),
            models.Index(fields=['status']),
            models.Index(fields=['priority']),
            models.Index(fields=['created_at']),
            models.Index(fields=['status', 'priority']),
        ]
    
    def __str__(self):
        return f"{self.ticket_number} - {self.subject}"
    
    def save(self, *args, **kwargs):
        """Auto-generate ticket number if not provided"""
        if not self.ticket_number:
            self.ticket_number = self.generate_ticket_number()
        super().save(*args, **kwargs)
    
    def generate_ticket_number(self):
        """Generate unique ticket number in format: TKT{YYYYMMDD}{###}"""
        today = timezone.now().date()
        year = today.strftime('%Y')
        month = today.strftime('%m')
        day = today.strftime('%d')
        
        # Get count of tickets created today
        today_tickets = Ticket.objects.filter(
            created_at__date=today
        ).count()
        
        return f"TKT{year}{month}{day}{str(today_tickets + 1).zfill(3)}"
    
    def get_status_display_class(self):
        """Get CSS/UI class for status display"""
        status_classes = {
            'open': 'primary',
            'in_progress': 'warning',
            'resolved': 'success',
            'closed': 'default',
        }
        return status_classes.get(self.status, 'default')
    
    def get_priority_display_class(self):
        """Get CSS/UI class for priority display"""
        priority_classes = {
            'low': 'default',
            'medium': 'primary',
            'high': 'warning',
            'urgent': 'error',
        }
        return priority_classes.get(self.priority, 'default')
    
    def can_be_updated(self):
        """Check if ticket can still be updated"""
        return self.status != 'closed'
    
    def mark_resolved(self):
        """Mark ticket as resolved"""
        self.status = 'resolved'
        self.resolved_at = timezone.now()
        self.save()
    
    def mark_closed(self):
        """Mark ticket as closed"""
        self.status = 'closed'
        self.closed_at = timezone.now()
        self.save()


class TicketComment(models.Model):
    """
    Comments on tickets - can be from customers or staff
    """
    
    ticket = models.ForeignKey(
        Ticket,
        on_delete=models.CASCADE,
        related_name='comments',
        help_text="Ticket this comment belongs to"
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        help_text="Person who wrote the comment"
    )
    comment = models.TextField(
        validators=[MaxLengthValidator(2000)],
        help_text="Comment text"
    )
    is_staff_comment = models.BooleanField(
        default=False,
        help_text="True if comment is from staff member"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Ticket Comment'
        verbose_name_plural = 'Ticket Comments'
        ordering = ['created_at']  # Oldest first
    
    def __str__(self):
        author_name = self.author.business_name or self.author.username
        return f"Comment by {author_name} on {self.ticket.ticket_number}"


class TicketHistory(models.Model):
    """
    Track changes to ticket status, priority, and other fields
    """
    
    ticket = models.ForeignKey(
        Ticket,
        on_delete=models.CASCADE,
        related_name='history',
        help_text="Ticket this history entry belongs to"
    )
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        help_text="User who made the change"
    )
    field_changed = models.CharField(
        max_length=50,
        help_text="Name of the field that was changed (status, priority, etc.)"
    )
    old_value = models.CharField(
        max_length=200,
        help_text="Previous value"
    )
    new_value = models.CharField(
        max_length=200,
        help_text="New value"
    )
    change_reason = models.TextField(
        blank=True,
        help_text="Optional reason for the change"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Ticket History'
        verbose_name_plural = 'Ticket Histories'
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.ticket.ticket_number} - {self.field_changed}: {self.old_value} → {self.new_value}"

