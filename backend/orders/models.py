from django.db import models
from django.core.validators import MinValueValidator
from django.conf import settings
from products.models import Product

class Order(models.Model):
    """Order model for customer orders"""
    
    ORDER_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('processing', 'Processing'),
        ('ready', 'Ready for Delivery'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]
    
    # Order Information
    order_number = models.CharField(max_length=20, unique=True, help_text="Auto-generated order number")
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders')
    
    # Order Details
    status = models.CharField(max_length=20, choices=ORDER_STATUS_CHOICES, default='pending')
    total_items = models.IntegerField(default=0, help_text="Total number of items in order")
    
    # Delivery Information
    delivery_address = models.TextField()
    delivery_instructions = models.TextField(blank=True)
    preferred_delivery_date = models.DateField(null=True, blank=True)
    actual_delivery_date = models.DateField(null=True, blank=True)
    
    # Business Information
    business_name = models.CharField(max_length=200)
    contact_person = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Order'
        verbose_name_plural = 'Orders'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['order_number']),
            models.Index(fields=['customer']),
            models.Index(fields=['status']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"Order {self.order_number} - {self.customer.business_name or self.customer.username}"
    
    def save(self, *args, **kwargs):
        """Auto-generate order number if not provided"""
        if not self.order_number:
            self.order_number = self.generate_order_number()
        super().save(*args, **kwargs)
    
    def generate_order_number(self):
        """Generate unique order number"""
        import datetime
        today = datetime.date.today()
        year = today.strftime('%Y')
        month = today.strftime('%m')
        day = today.strftime('%d')
        
        # Get count of orders for today
        today_orders = Order.objects.filter(
            created_at__date=today
        ).count()
        
        return f"DD{year}{month}{day}{str(today_orders + 1).zfill(3)}"
    
    def get_status_display_class(self):
        """Get CSS class for status display"""
        status_classes = {
            'pending': 'badge-warning',
            'confirmed': 'badge-info',
            'processing': 'badge-primary',
            'ready': 'badge-success',
            'delivered': 'badge-success',
            'cancelled': 'badge-danger',
        }
        return status_classes.get(self.status, 'badge-secondary')
    
    def can_be_cancelled(self):
        """Check if order can be cancelled"""
        return self.status in ['pending', 'confirmed']
    
    def get_total_items(self):
        """Get total number of items in order"""
        return sum(item.quantity for item in self.items.all())

class OrderItem(models.Model):
    """Individual item in an order"""
    
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(
        validators=[MinValueValidator(1)]
    )
    
    class Meta:
        verbose_name = 'Order Item'
        verbose_name_plural = 'Order Items'
        ordering = ['id']
    
    def __str__(self):
        return f"{self.quantity} x {self.product.name} in Order {self.order.order_number}"
    
    def get_display_total(self):
        """Get formatted total quantity"""
        return f"{self.quantity} {self.product.unit}"
