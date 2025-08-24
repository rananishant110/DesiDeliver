from django.contrib import admin
from .models import Cart, CartItem

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    """Admin configuration for Cart model"""
    
    list_display = ('user', 'get_total_items', 'get_total_amount', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('user__username', 'user__business_name')
    ordering = ('-created_at',)
    
    fieldsets = (
        (None, {
            'fields': ('user', 'is_active')
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at')
    
    def get_total_items(self, obj):
        return obj.get_total_items()
    get_total_items.short_description = 'Total Items'
    
    def get_total_amount(self, obj):
        return obj.get_total_amount()
    get_total_amount.short_description = 'Total Items'

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    """Admin configuration for CartItem model"""
    
    list_display = ('cart', 'product', 'quantity', 'get_total_price', 'added_at')
    list_filter = ('added_at',)
    search_fields = ('cart__user__username', 'product__name', 'product__item_code')
    ordering = ('-added_at',)
    
    fieldsets = (
        (None, {
            'fields': ('cart', 'product', 'quantity')
        }),
    )
    
    readonly_fields = ('added_at', 'updated_at')
    
    def get_total_price(self, obj):
        return obj.get_display_total()
    get_total_price.short_description = 'Total Quantity'
