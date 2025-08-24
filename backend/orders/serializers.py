from rest_framework import serializers
from .models import Order, OrderItem
from products.serializers import ProductListSerializer
from users.serializers import UserProfileSerializer

class OrderItemSerializer(serializers.ModelSerializer):
    """Serializer for order items"""
    product = ProductListSerializer(read_only=True)
    product_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'product_id', 'quantity']
        read_only_fields = ['id', 'product']
    
    def validate_quantity(self, value):
        if value < 1:
            raise serializers.ValidationError("Quantity must be at least 1")
        return value

class OrderSerializer(serializers.ModelSerializer):
    """Serializer for orders"""
    items = OrderItemSerializer(many=True, read_only=True)
    customer = UserProfileSerializer(read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    can_cancel = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'customer', 'status', 'status_display',
            'total_items', 'delivery_address', 'delivery_instructions',
            'preferred_delivery_date', 'actual_delivery_date',
            'business_name', 'contact_person', 'phone_number',
            'created_at', 'updated_at', 'items', 'can_cancel'
        ]
        read_only_fields = [
            'id', 'order_number', 'customer', 'created_at', 'updated_at',
            'status_display', 'can_cancel'
        ]

class CreateOrderSerializer(serializers.Serializer):
    """Serializer for creating new orders"""
    delivery_address = serializers.CharField(max_length=500)
    delivery_instructions = serializers.CharField(max_length=500, required=False, allow_blank=True)
    preferred_delivery_date = serializers.DateField(required=False, allow_null=True)
    business_name = serializers.CharField(max_length=200)
    contact_person = serializers.CharField(max_length=100)
    phone_number = serializers.CharField(max_length=20)
    
    def validate_preferred_delivery_date(self, value):
        """Validate delivery date is not in the past"""
        if value:
            from datetime import date
            if value < date.today():
                raise serializers.ValidationError("Preferred delivery date cannot be in the past")
        return value

class OrderStatusUpdateSerializer(serializers.Serializer):
    """Serializer for updating order status"""
    status = serializers.ChoiceField(choices=Order.ORDER_STATUS_CHOICES)
    
    def validate_status(self, value):
        """Validate status transition"""
        # Add business logic for status transitions if needed
        return value

class OrderSummarySerializer(serializers.ModelSerializer):
    """Simplified order serializer for lists"""
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    item_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'status', 'status_display',
            'total_items', 'business_name', 'created_at', 'item_count'
        ]
        read_only_fields = ['id', 'order_number', 'created_at', 'status_display', 'item_count']
    
    def get_item_count(self, obj):
        return obj.items.count()
