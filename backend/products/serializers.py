from rest_framework import serializers
from .models import Category, Product


class CategorySerializer(serializers.ModelSerializer):
    """Serializer for Category model"""
    
    class Meta:
        model = Category
        fields = [
            'id', 'name', 'description', 'slug', 
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ProductListSerializer(serializers.ModelSerializer):
    """Serializer for product listing (minimal data)"""
    
    category = CategorySerializer(read_only=True)
    
    class Meta:
        model = Product
        fields = [
            'id', 'item_code', 'name', 'description', 'category',
            'unit', 'min_order_quantity', 'in_stock', 'stock_quantity',
            'brand', 'origin', 'is_active'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ProductDetailSerializer(serializers.ModelSerializer):
    """Serializer for detailed product view"""
    
    category = CategorySerializer(read_only=True)
    
    class Meta:
        model = Product
        fields = [
            'id', 'item_code', 'name', 'description', 'category',
            'unit', 'min_order_quantity', 'in_stock', 'stock_quantity',
            'brand', 'origin', 'weight', 'is_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ProductSearchSerializer(serializers.Serializer):
    """Serializer for product search parameters"""
    
    search = serializers.CharField(required=False, allow_blank=True)
    category = serializers.IntegerField(required=False)
    in_stock = serializers.BooleanField(required=False)
    brand = serializers.CharField(required=False, allow_blank=True)
    origin = serializers.CharField(required=False, allow_blank=True)
    page = serializers.IntegerField(required=False, min_value=1, default=1)
    page_size = serializers.IntegerField(required=False, min_value=1, max_value=100, default=20)
