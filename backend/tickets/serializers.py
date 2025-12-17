from rest_framework import serializers
from .models import Ticket, TicketComment, TicketHistory
from users.models import CustomUser
from orders.models import Order


class UserBasicSerializer(serializers.ModelSerializer):
    """Basic user information for nested serialization"""
    
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'business_name', 'is_staff']


class OrderBasicSerializer(serializers.ModelSerializer):
    """Basic order information for nested serialization"""
    
    class Meta:
        model = Order
        fields = ['id', 'order_number', 'status', 'created_at']


class TicketCommentSerializer(serializers.ModelSerializer):
    """Serializer for ticket comments"""
    
    author = UserBasicSerializer(read_only=True)
    
    class Meta:
        model = TicketComment
        fields = [
            'id',
            'ticket',
            'author',
            'comment',
            'is_staff_comment',
            'created_at'
        ]
        read_only_fields = ['id', 'author', 'is_staff_comment', 'created_at']


class TicketHistorySerializer(serializers.ModelSerializer):
    """Serializer for ticket history entries"""
    
    changed_by = UserBasicSerializer(read_only=True)
    
    class Meta:
        model = TicketHistory
        fields = [
            'id',
            'ticket',
            'changed_by',
            'field_changed',
            'old_value',
            'new_value',
            'change_reason',
            'created_at'
        ]
        read_only_fields = [
            'id',
            'ticket',
            'changed_by',
            'field_changed',
            'old_value',
            'new_value',
            'change_reason',
            'created_at'
        ]


class TicketListSerializer(serializers.ModelSerializer):
    """Serializer for ticket list view (summary)"""
    
    customer = UserBasicSerializer(read_only=True)
    order = OrderBasicSerializer(read_only=True)
    
    class Meta:
        model = Ticket
        fields = [
            'id',
            'ticket_number',
            'customer',
            'order',
            'subject',
            'category',
            'priority',
            'status',
            'created_at',
            'updated_at'
        ]
        read_only_fields = [
            'id',
            'ticket_number',
            'customer',
            'order',
            'created_at',
            'updated_at'
        ]


class TicketSerializer(serializers.ModelSerializer):
    """Detailed serializer for ticket with nested comments and history"""
    
    customer = UserBasicSerializer(read_only=True)
    order = OrderBasicSerializer(read_only=True)
    comments = TicketCommentSerializer(many=True, read_only=True)
    history = TicketHistorySerializer(many=True, read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    can_update = serializers.BooleanField(source='can_be_updated', read_only=True)
    
    class Meta:
        model = Ticket
        fields = [
            'id',
            'ticket_number',
            'customer',
            'order',
            'subject',
            'description',
            'category',
            'priority',
            'priority_display',
            'status',
            'status_display',
            'created_at',
            'updated_at',
            'resolved_at',
            'closed_at',
            'comments',
            'history',
            'can_update'
        ]
        read_only_fields = [
            'id',
            'ticket_number',
            'customer',
            'created_at',
            'updated_at',
            'resolved_at',
            'closed_at',
            'comments',
            'history',
            'status_display',
            'priority_display',
            'can_update'
        ]


class CreateTicketSerializer(serializers.ModelSerializer):
    """Serializer for creating new tickets"""
    
    order_id = serializers.IntegerField(required=False, allow_null=True)
    
    class Meta:
        model = Ticket
        fields = [
            'subject',
            'description',
            'category',
            'priority',
            'order_id'
        ]
    
    def validate_subject(self, value):
        """Validate subject length"""
        if len(value) < 5:
            raise serializers.ValidationError("Subject must be at least 5 characters long")
        if len(value) > 200:
            raise serializers.ValidationError("Subject must not exceed 200 characters")
        return value
    
    def validate_description(self, value):
        """Validate description length"""
        if len(value) < 20:
            raise serializers.ValidationError("Description must be at least 20 characters long")
        if len(value) > 2000:
            raise serializers.ValidationError("Description must not exceed 2000 characters")
        return value
    
    def validate_order_id(self, value):
        """Validate that order exists and belongs to the requesting user"""
        if value is None:
            return None
        
        request = self.context.get('request')
        if not request:
            raise serializers.ValidationError("Request context is required")
        
        try:
            order = Order.objects.get(id=value)
        except Order.DoesNotExist:
            raise serializers.ValidationError("Order not found")
        
        # Check if order belongs to the requesting user (unless staff)
        if not request.user.is_staff and order.customer != request.user:
            raise serializers.ValidationError("You can only create tickets for your own orders")
        
        return value
    
    def create(self, validated_data):
        """Create ticket with auto-generated ticket number"""
        order_id = validated_data.pop('order_id', None)
        
        # Get the request user from context
        request = self.context.get('request')
        customer = request.user
        
        # Get order if provided
        order = None
        if order_id:
            try:
                order = Order.objects.get(id=order_id)
            except Order.DoesNotExist:
                pass
        
        # Create ticket
        ticket = Ticket.objects.create(
            customer=customer,
            order=order,
            **validated_data
        )
        
        return ticket


class UpdateTicketStatusSerializer(serializers.Serializer):
    """Serializer for updating ticket status"""
    
    status = serializers.ChoiceField(choices=Ticket.STATUS_CHOICES)
    reason = serializers.CharField(required=False, allow_blank=True, max_length=500)
    
    def validate_status(self, value):
        """Validate status transition"""
        ticket = self.context.get('ticket')
        if not ticket:
            raise serializers.ValidationError("Ticket context is required")
        
        current_status = ticket.status
        
        # Define allowed transitions
        allowed_transitions = {
            'open': ['in_progress', 'closed'],
            'in_progress': ['resolved', 'open', 'closed'],
            'resolved': ['closed', 'in_progress'],  # Can reopen or close
            'closed': []  # Cannot transition from closed
        }
        
        if current_status == 'closed':
            raise serializers.ValidationError("Cannot change status of closed tickets")
        
        if value not in allowed_transitions.get(current_status, []):
            raise serializers.ValidationError(
                f"Cannot transition from '{current_status}' to '{value}'"
            )
        
        return value


class UpdateTicketPrioritySerializer(serializers.Serializer):
    """Serializer for updating ticket priority"""
    
    priority = serializers.ChoiceField(choices=Ticket.PRIORITY_CHOICES)
    reason = serializers.CharField(required=False, allow_blank=True, max_length=500)


class AddCommentSerializer(serializers.Serializer):
    """Serializer for adding comments to tickets"""
    
    comment = serializers.CharField(max_length=2000, required=True)
    
    def validate_comment(self, value):
        """Validate comment"""
        if len(value.strip()) == 0:
            raise serializers.ValidationError("Comment cannot be empty")
        if len(value) > 2000:
            raise serializers.ValidationError("Comment must not exceed 2000 characters")
        return value.strip()
