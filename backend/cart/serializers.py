from rest_framework import serializers
from .models import Cart, CartItem
from products.serializers import ProductListSerializer


class CartItemSerializer(serializers.ModelSerializer):
    product = ProductListSerializer(read_only=True)
    product_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = CartItem
        fields = [
            'id', 'product', 'product_id', 'quantity', 
            'added_at', 'updated_at'
        ]
        read_only_fields = ['id', 'added_at', 'updated_at']

    def validate_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError("Quantity must be greater than 0")
        return value

    def validate(self, data):
        # Check if product exists and is active
        product_id = data.get('product_id')
        if product_id:
            try:
                from products.models import Product
                product = Product.objects.get(id=product_id, is_active=True)
                data['product'] = product
            except Product.DoesNotExist:
                raise serializers.ValidationError("Product not found or inactive")
        
        return data


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_items = serializers.ReadOnlyField()
    total_quantity = serializers.ReadOnlyField()
    
    class Meta:
        model = Cart
        fields = [
            'id', 'user', 'items', 'total_items', 'total_quantity',
            'created_at', 'updated_at', 'is_active'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']


class AddToCartSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1)
    
    def validate_quantity(self, value):
        if value < 1:
            raise serializers.ValidationError("Quantity must be at least 1")
        return value


class UpdateCartItemSerializer(serializers.Serializer):
    quantity = serializers.IntegerField(min_value=1)
    
    def validate_quantity(self, value):
        if value < 1:
            raise serializers.ValidationError("Quantity must be at least 1")
        return value
