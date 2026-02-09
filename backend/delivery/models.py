from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.conf import settings
from orders.models import Order
from decimal import Decimal


class DeliveryPersonnel(models.Model):
    """Model for delivery drivers/personnel"""
    
    VEHICLE_TYPE_CHOICES = [
        ('bike', 'Bike'),
        ('scooter', 'Scooter'),
        ('car', 'Car'),
        ('van', 'Van'),
        ('truck', 'Truck'),
    ]
    
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('on_delivery', 'On Delivery'),
        ('off_duty', 'Off Duty'),
    ]
    
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='delivery_profile'
    )
    employee_id = models.CharField(max_length=20, unique=True, help_text="Unique employee identifier")
    phone_number = models.CharField(max_length=20)
    vehicle_type = models.CharField(max_length=20, choices=VEHICLE_TYPE_CHOICES)
    vehicle_number = models.CharField(max_length=20)
    license_number = models.CharField(max_length=50)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    
    # Current location
    current_latitude = models.DecimalField(
        max_digits=9, 
        decimal_places=6, 
        null=True, 
        blank=True,
        help_text="Current latitude position"
    )
    current_longitude = models.DecimalField(
        max_digits=9, 
        decimal_places=6, 
        null=True, 
        blank=True,
        help_text="Current longitude position"
    )
    last_location_update = models.DateTimeField(null=True, blank=True)
    
    # Performance metrics
    total_deliveries = models.IntegerField(default=0)
    successful_deliveries = models.IntegerField(default=0)
    average_rating = models.DecimalField(
        max_digits=3, 
        decimal_places=2, 
        default=Decimal('0.00'),
        validators=[MinValueValidator(0), MaxValueValidator(5)]
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Delivery Personnel'
        verbose_name_plural = 'Delivery Personnel'
        ordering = ['user__first_name', 'user__last_name']
        indexes = [
            models.Index(fields=['employee_id']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.employee_id}"
    
    def update_location(self, latitude, longitude):
        """Update current location"""
        from django.utils import timezone
        self.current_latitude = latitude
        self.current_longitude = longitude
        self.last_location_update = timezone.now()
        self.save(update_fields=['current_latitude', 'current_longitude', 'last_location_update'])


class DeliveryTracking(models.Model):
    """Model for tracking deliveries"""
    
    STATUS_CHOICES = [
        ('assigned', 'Assigned'),
        ('picked_up', 'Picked Up'),
        ('in_transit', 'In Transit'),
        ('nearby', 'Nearby'),
        ('delivered', 'Delivered'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]
    
    order = models.OneToOneField(
        Order, 
        on_delete=models.CASCADE, 
        related_name='tracking'
    )
    driver = models.ForeignKey(
        DeliveryPersonnel, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='deliveries'
    )
    
    # Status tracking
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='assigned')
    
    # Location tracking
    pickup_latitude = models.DecimalField(
        max_digits=9, 
        decimal_places=6,
        help_text="Pickup location latitude"
    )
    pickup_longitude = models.DecimalField(
        max_digits=9, 
        decimal_places=6,
        help_text="Pickup location longitude"
    )
    delivery_latitude = models.DecimalField(
        max_digits=9, 
        decimal_places=6,
        help_text="Delivery destination latitude"
    )
    delivery_longitude = models.DecimalField(
        max_digits=9, 
        decimal_places=6,
        help_text="Delivery destination longitude"
    )
    
    # Current driver location (updated in real-time)
    current_latitude = models.DecimalField(
        max_digits=9, 
        decimal_places=6, 
        null=True, 
        blank=True,
        help_text="Driver's current latitude"
    )
    current_longitude = models.DecimalField(
        max_digits=9, 
        decimal_places=6, 
        null=True, 
        blank=True,
        help_text="Driver's current longitude"
    )
    
    # Time tracking
    assigned_at = models.DateTimeField(auto_now_add=True)
    picked_up_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    estimated_delivery_time = models.DateTimeField(null=True, blank=True)
    
    # Distance tracking (in kilometers)
    total_distance = models.DecimalField(
        max_digits=8, 
        decimal_places=2, 
        null=True, 
        blank=True,
        help_text="Total distance in kilometers"
    )
    
    # Delivery notes and proof
    delivery_notes = models.TextField(blank=True)
    proof_of_delivery_photo = models.ImageField(
        upload_to='delivery_proofs/', 
        null=True, 
        blank=True
    )
    customer_signature = models.ImageField(
        upload_to='delivery_signatures/', 
        null=True, 
        blank=True
    )
    
    # Customer feedback
    customer_rating = models.IntegerField(
        null=True, 
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    customer_feedback = models.TextField(blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Delivery Tracking'
        verbose_name_plural = 'Delivery Trackings'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['order']),
            models.Index(fields=['driver']),
            models.Index(fields=['status']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"Tracking for Order {self.order.order_number}"
    
    def update_driver_location(self, latitude, longitude):
        """Update driver's current location"""
        from django.utils import timezone
        self.current_latitude = latitude
        self.current_longitude = longitude
        self.updated_at = timezone.now()
        self.save(update_fields=['current_latitude', 'current_longitude', 'updated_at'])
        
        # Also update driver's location
        if self.driver:
            self.driver.update_location(latitude, longitude)
    
    def mark_picked_up(self):
        """Mark order as picked up"""
        from django.utils import timezone
        self.status = 'picked_up'
        self.picked_up_at = timezone.now()
        self.save(update_fields=['status', 'picked_up_at'])
    
    def mark_delivered(self, notes='', photo=None, signature=None):
        """Mark order as delivered"""
        from django.utils import timezone
        self.status = 'delivered'
        self.delivered_at = timezone.now()
        self.delivery_notes = notes
        if photo:
            self.proof_of_delivery_photo = photo
        if signature:
            self.customer_signature = signature
        self.save()
        
        # Update order status
        self.order.status = 'delivered'
        self.order.actual_delivery_date = timezone.now().date()
        self.order.save()
        
        # Update driver status and stats
        if self.driver:
            self.driver.status = 'available'
            self.driver.total_deliveries += 1
            self.driver.successful_deliveries += 1
            self.driver.save()


class DeliveryRoute(models.Model):
    """Model for tracking delivery route history"""
    
    tracking = models.ForeignKey(
        DeliveryTracking, 
        on_delete=models.CASCADE, 
        related_name='route_points'
    )
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    recorded_at = models.DateTimeField(auto_now_add=True)
    speed = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        null=True, 
        blank=True,
        help_text="Speed in km/h"
    )
    
    class Meta:
        verbose_name = 'Delivery Route Point'
        verbose_name_plural = 'Delivery Route Points'
        ordering = ['recorded_at']
        indexes = [
            models.Index(fields=['tracking', 'recorded_at']),
        ]
    
    def __str__(self):
        return f"Route point for {self.tracking} at {self.recorded_at}"


class DeliveryStatusHistory(models.Model):
    """Model for tracking delivery status changes"""
    
    tracking = models.ForeignKey(
        DeliveryTracking, 
        on_delete=models.CASCADE, 
        related_name='status_history'
    )
    status = models.CharField(max_length=20)
    notes = models.TextField(blank=True)
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True,
        related_name='delivery_status_changes'
    )
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Delivery Status History'
        verbose_name_plural = 'Delivery Status Histories'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['tracking', 'timestamp']),
        ]
    
    def __str__(self):
        return f"{self.tracking} - {self.status} at {self.timestamp}"
