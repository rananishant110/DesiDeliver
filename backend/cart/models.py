from django.db import models
from django.core.validators import MinValueValidator
from django.conf import settings
from products.models import Product

class Cart(models.Model):
    """Shopping cart model for users"""
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='carts')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = 'Cart'
        verbose_name_plural = 'Carts'
        ordering = ['-updated_at']
    
    def __str__(self):
        return f"Cart for {self.user.business_name or self.user.username}"
    
    @property
    def total_items(self):
        """Get total number of items in cart"""
        return sum(item.quantity for item in self.items.all())
    
    @property
    def total_quantity(self):
        """Calculate total cart items count"""
        return sum(item.quantity for item in self.items.all())
    
    def get_total_items(self):
        """Get total number of items in cart (legacy method)"""
        return self.total_items
    
    def get_total_amount(self):
        """Calculate total cart items count (legacy method)"""
        return self.total_quantity
    
    def clear(self):
        """Remove all items from cart"""
        self.items.all().delete()
        self.save()

class CartItem(models.Model):
    """Individual item in shopping cart"""
    
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(
        validators=[MinValueValidator(1)]
    )
    added_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Cart Item'
        verbose_name_plural = 'Cart Items'
        unique_together = ['cart', 'product']
        ordering = ['-added_at']
    
    def __str__(self):
        return f"{self.quantity} x {self.product.name} in {self.cart}"
    
    def get_total_quantity(self):
        """Calculate total quantity for this item"""
        return self.quantity
    
    def get_display_total(self):
        """Get formatted total quantity"""
        return f"{self.quantity} {self.product.unit}"
    
    def is_available(self):
        """Check if product is still available"""
        return self.product.is_available()
    
    def validate_quantity(self):
        """Validate quantity against product constraints"""
        if self.quantity < self.product.min_order_quantity:
            return False, f"Minimum order quantity is {self.product.min_order_quantity} {self.product.unit}"
        if self.product.stock_quantity < self.quantity:
            return False, f"Only {self.product.stock_quantity} {self.product.unit} available"
        return True, "Valid quantity"
