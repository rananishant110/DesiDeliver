from django.contrib import admin
from .models import Order, OrderItem

class OrderItemInline(admin.TabularInline):
    """Inline admin for OrderItem"""
    
    model = OrderItem
    extra = 0
    fields = ('product', 'quantity')

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """Admin configuration for Order model"""
    
    list_display = ('order_number', 'customer', 'status', 'total_items', 'get_total_items', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('order_number', 'customer__username', 'customer__business_name', 'business_name')
    ordering = ('-created_at',)
    readonly_fields = ('order_number', 'created_at', 'updated_at')
    
    fieldsets = (
        ('Order Information', {
            'fields': ('order_number', 'customer', 'status', 'total_items')
        }),
        ('Delivery Information', {
            'fields': ('delivery_address', 'delivery_instructions', 'preferred_delivery_date', 'actual_delivery_date')
        }),
        ('Business Information', {
            'fields': ('business_name', 'contact_person', 'phone_number')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    inlines = [OrderItemInline]
    
    def get_total_items(self, obj):
        return obj.get_total_items()
    get_total_items.short_description = 'Total Items'
    
    def get_queryset(self, request):
        """Optimize queries with select_related"""
        return super().get_queryset(request).select_related('customer')

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    """Admin configuration for OrderItem model"""
    
    list_display = ('order', 'product', 'quantity')
    list_filter = ('order__status',)
    search_fields = ('order__order_number', 'product__name', 'product__item_code')
    ordering = ('-order__created_at',)
    
    fieldsets = (
        (None, {
            'fields': ('order', 'product', 'quantity')
        }),
    )
    
    def get_queryset(self, request):
        """Optimize queries with select_related"""
        return super().get_queryset(request).select_related('order', 'product')
