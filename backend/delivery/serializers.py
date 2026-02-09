from rest_framework import serializers
from .models import DeliveryPersonnel, DeliveryTracking, DeliveryRoute, DeliveryStatusHistory
from orders.serializers import OrderSerializer
from django.contrib.auth import get_user_model

User = get_user_model()


class UserBasicSerializer(serializers.ModelSerializer):
    """Basic user serializer for delivery personnel"""
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'full_name', 'phone_number']
    
    def get_full_name(self, obj):
        return obj.get_full_name() or obj.username


class DeliveryPersonnelSerializer(serializers.ModelSerializer):
    """Serializer for delivery personnel"""
    user = UserBasicSerializer(read_only=True)
    user_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = DeliveryPersonnel
        fields = [
            'id', 'user', 'user_id', 'employee_id', 'phone_number',
            'vehicle_type', 'vehicle_number', 'license_number', 'status',
            'current_latitude', 'current_longitude', 'last_location_update',
            'total_deliveries', 'successful_deliveries', 'average_rating',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['total_deliveries', 'successful_deliveries', 'average_rating', 
                           'created_at', 'updated_at', 'last_location_update']


class DeliveryPersonnelListSerializer(serializers.ModelSerializer):
    """Simplified serializer for listing delivery personnel"""
    user = UserBasicSerializer(read_only=True)
    
    class Meta:
        model = DeliveryPersonnel
        fields = ['id', 'user', 'employee_id', 'vehicle_type', 'status', 
                 'total_deliveries', 'average_rating']


class DeliveryRouteSerializer(serializers.ModelSerializer):
    """Serializer for delivery route points"""
    
    class Meta:
        model = DeliveryRoute
        fields = ['id', 'latitude', 'longitude', 'speed', 'recorded_at']
        read_only_fields = ['recorded_at']


class DeliveryStatusHistorySerializer(serializers.ModelSerializer):
    """Serializer for delivery status history"""
    changed_by_name = serializers.SerializerMethodField()
    
    class Meta:
        model = DeliveryStatusHistory
        fields = ['id', 'status', 'notes', 'changed_by', 'changed_by_name', 'timestamp']
        read_only_fields = ['timestamp']
    
    def get_changed_by_name(self, obj):
        if obj.changed_by:
            return obj.changed_by.get_full_name() or obj.changed_by.username
        return None


class DeliveryTrackingSerializer(serializers.ModelSerializer):
    """Serializer for delivery tracking"""
    driver = DeliveryPersonnelListSerializer(read_only=True)
    driver_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    order = OrderSerializer(read_only=True)
    order_id = serializers.IntegerField(write_only=True)
    status_history = DeliveryStatusHistorySerializer(many=True, read_only=True)
    route_points = DeliveryRouteSerializer(many=True, read_only=True)
    
    class Meta:
        model = DeliveryTracking
        fields = [
            'id', 'order', 'order_id', 'driver', 'driver_id', 'status',
            'pickup_latitude', 'pickup_longitude',
            'delivery_latitude', 'delivery_longitude',
            'current_latitude', 'current_longitude',
            'assigned_at', 'picked_up_at', 'delivered_at', 'estimated_delivery_time',
            'total_distance', 'delivery_notes',
            'proof_of_delivery_photo', 'customer_signature',
            'customer_rating', 'customer_feedback',
            'status_history', 'route_points',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['assigned_at', 'created_at', 'updated_at']
    
    def validate(self, data):
        """Custom validation"""
        # Ensure pickup and delivery coordinates are provided
        if not all([
            data.get('pickup_latitude'),
            data.get('pickup_longitude'),
            data.get('delivery_latitude'),
            data.get('delivery_longitude')
        ]):
            raise serializers.ValidationError(
                "Pickup and delivery coordinates are required"
            )
        return data


class DeliveryTrackingListSerializer(serializers.ModelSerializer):
    """Simplified serializer for listing delivery trackings"""
    driver = DeliveryPersonnelListSerializer(read_only=True)
    order_number = serializers.CharField(source='order.order_number', read_only=True)
    customer_name = serializers.SerializerMethodField()
    
    class Meta:
        model = DeliveryTracking
        fields = [
            'id', 'order', 'order_number', 'customer_name', 'driver', 'status',
            'current_latitude', 'current_longitude',
            'assigned_at', 'estimated_delivery_time', 'delivered_at'
        ]
    
    def get_customer_name(self, obj):
        return obj.order.customer.get_full_name() or obj.order.customer.username


class LocationUpdateSerializer(serializers.Serializer):
    """Serializer for location updates"""
    latitude = serializers.DecimalField(max_digits=9, decimal_places=6)
    longitude = serializers.DecimalField(max_digits=9, decimal_places=6)
    speed = serializers.DecimalField(max_digits=5, decimal_places=2, required=False, allow_null=True)


class DeliveryProofSerializer(serializers.Serializer):
    """Serializer for delivery proof"""
    notes = serializers.CharField(required=False, allow_blank=True)
    proof_photo = serializers.ImageField(required=False, allow_null=True)
    signature = serializers.ImageField(required=False, allow_null=True)


class CustomerFeedbackSerializer(serializers.Serializer):
    """Serializer for customer feedback"""
    rating = serializers.IntegerField(min_value=1, max_value=5)
    feedback = serializers.CharField(required=False, allow_blank=True)
