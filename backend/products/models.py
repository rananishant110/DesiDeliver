from django.db import models
from django.core.validators import MinValueValidator, DecimalValidator

class Category(models.Model):
    """Product category model"""
    
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    slug = models.SlugField(max_length=100, unique=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
        ordering = ['name']
    
    def __str__(self):
        return self.name

class Product(models.Model):
    """Product model for Indian groceries and supplies"""
    
    # Basic Information
    item_code = models.CharField(max_length=50, unique=True, help_text="Unique product identifier")
    name = models.CharField(max_length=200)
    description = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    
    # Units and Quantities
    unit = models.CharField(max_length=50, help_text="e.g., kg, lb, piece, pack")
    min_order_quantity = models.DecimalField(
        max_digits=8, 
        decimal_places=2,
        default=1.0,
        validators=[MinValueValidator(0.01)]
    )
    
    # Inventory
    in_stock = models.BooleanField(default=True)
    stock_quantity = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        default=0.0,
        validators=[MinValueValidator(0.0)]
    )
    
    # Product Details
    brand = models.CharField(max_length=100, blank=True)
    origin = models.CharField(max_length=100, blank=True, help_text="Country of origin")
    weight = models.DecimalField(
        max_digits=8, 
        decimal_places=2,
        blank=True,
        null=True,
        help_text="Weight in grams"
    )
    
    # Status and Timestamps
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Product'
        verbose_name_plural = 'Products'
        ordering = ['category', 'name']
        indexes = [
            models.Index(fields=['item_code']),
            models.Index(fields=['category']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"{self.item_code} - {self.name}"
    
    def is_available(self):
        """Check if product is available for ordering"""
        return self.is_active and self.in_stock and self.stock_quantity > 0
    
    def get_stock_status(self):
        """Get human-readable stock status"""
        if not self.in_stock:
            return "Out of Stock"
        elif self.stock_quantity <= 0:
            return "Out of Stock"
        elif self.stock_quantity < 10:
            return "Low Stock"
        else:
            return "In Stock"
