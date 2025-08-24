from django.contrib import admin
from .models import Category, Product

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Admin configuration for Category model"""
    
    list_display = ('name', 'slug', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    ordering = ('name',)
    
    fieldsets = (
        (None, {
            'fields': ('name', 'slug', 'description')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at')

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """Admin configuration for Product model"""
    
    list_display = ('item_code', 'name', 'category', 'unit', 'in_stock', 'is_active', 'created_at')
    list_filter = ('category', 'in_stock', 'is_active', 'created_at')
    search_fields = ('item_code', 'name', 'description', 'brand')
    list_editable = ('in_stock', 'is_active')
    ordering = ('category', 'name')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('item_code', 'name', 'description', 'category')
        }),
        ('Units & Quantities', {
            'fields': ('unit', 'min_order_quantity')
        }),
        ('Inventory', {
            'fields': ('in_stock', 'stock_quantity')
        }),
        ('Product Details', {
            'fields': ('brand', 'origin', 'weight')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at')
    
    def get_queryset(self, request):
        """Optimize queries with select_related"""
        return super().get_queryset(request).select_related('category')
