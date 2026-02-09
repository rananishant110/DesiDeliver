from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.db.models import Q
from .models import DeliveryPersonnel, DeliveryTracking, DeliveryRoute, DeliveryStatusHistory
from .serializers import (
    DeliveryPersonnelSerializer, DeliveryPersonnelListSerializer,
    DeliveryTrackingSerializer, DeliveryTrackingListSerializer,
    DeliveryRouteSerializer, DeliveryStatusHistorySerializer,
    LocationUpdateSerializer, DeliveryProofSerializer, CustomerFeedbackSerializer
)


class DeliveryPersonnelViewSet(viewsets.ModelViewSet):
    """ViewSet for delivery personnel management"""
    queryset = DeliveryPersonnel.objects.select_related('user').all()
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return DeliveryPersonnelListSerializer
        return DeliveryPersonnelSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by status
        status_param = self.request.query_params.get('status')
        if status_param:
            queryset = queryset.filter(status=status_param)
        
        # Filter available drivers
        available = self.request.query_params.get('available')
        if available == 'true':
            queryset = queryset.filter(status='available')
        
        return queryset
    
    @action(detail=True, methods=['patch'])
    def update_location(self, request, pk=None):
        """Update driver's current location"""
        driver = self.get_object()
        serializer = LocationUpdateSerializer(data=request.data)
        
        if serializer.is_valid():
            driver.update_location(
                serializer.validated_data['latitude'],
                serializer.validated_data['longitude']
            )
            return Response({
                'message': 'Location updated successfully',
                'latitude': driver.current_latitude,
                'longitude': driver.current_longitude,
                'timestamp': driver.last_location_update
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['patch'])
    def update_status(self, request, pk=None):
        """Update driver's status"""
        driver = self.get_object()
        new_status = request.data.get('status')
        
        if new_status not in dict(DeliveryPersonnel.STATUS_CHOICES):
            return Response(
                {'error': 'Invalid status'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        driver.status = new_status
        driver.save(update_fields=['status'])
        
        return Response({
            'message': 'Status updated successfully',
            'status': driver.status
        })
    
    @action(detail=True, methods=['get'])
    def current_delivery(self, request, pk=None):
        """Get driver's current active delivery"""
        driver = self.get_object()
        
        active_delivery = DeliveryTracking.objects.filter(
            driver=driver,
            status__in=['assigned', 'picked_up', 'in_transit', 'nearby']
        ).select_related('order').first()
        
        if active_delivery:
            serializer = DeliveryTrackingSerializer(active_delivery)
            return Response(serializer.data)
        
        return Response({'message': 'No active delivery'}, status=status.HTTP_404_NOT_FOUND)


class DeliveryTrackingViewSet(viewsets.ModelViewSet):
    """ViewSet for delivery tracking management"""
    queryset = DeliveryTracking.objects.select_related('order', 'driver', 'driver__user').all()
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return DeliveryTrackingListSerializer
        return DeliveryTrackingSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        
        # Filter by user role
        if user.is_staff:
            # Staff can see all deliveries
            pass
        else:
            # Customers can only see their own orders
            queryset = queryset.filter(order__customer=user)
        
        # Filter by status
        status_param = self.request.query_params.get('status')
        if status_param:
            queryset = queryset.filter(status=status_param)
        
        # Filter by driver
        driver_id = self.request.query_params.get('driver')
        if driver_id:
            queryset = queryset.filter(driver_id=driver_id)
        
        # Filter active deliveries
        active_only = self.request.query_params.get('active')
        if active_only == 'true':
            queryset = queryset.filter(
                status__in=['assigned', 'picked_up', 'in_transit', 'nearby']
            )
        
        return queryset.prefetch_related('status_history', 'route_points')
    
    def perform_create(self, serializer):
        """Create delivery tracking and update order status"""
        tracking = serializer.save()
        
        # Update order status
        tracking.order.status = 'ready'
        tracking.order.save()
        
        # Create initial status history
        DeliveryStatusHistory.objects.create(
            tracking=tracking,
            status='assigned',
            notes='Delivery assigned',
            changed_by=self.request.user
        )
        
        # Update driver status if assigned
        if tracking.driver:
            tracking.driver.status = 'on_delivery'
            tracking.driver.save()
    
    @action(detail=True, methods=['patch'])
    def update_location(self, request, pk=None):
        """Update delivery location (driver's current position)"""
        tracking = self.get_object()
        serializer = LocationUpdateSerializer(data=request.data)
        
        if serializer.is_valid():
            latitude = serializer.validated_data['latitude']
            longitude = serializer.validated_data['longitude']
            speed = serializer.validated_data.get('speed')
            
            # Update tracking location
            tracking.update_driver_location(latitude, longitude)
            
            # Record route point
            DeliveryRoute.objects.create(
                tracking=tracking,
                latitude=latitude,
                longitude=longitude,
                speed=speed
            )
            
            return Response({
                'message': 'Location updated successfully',
                'latitude': tracking.current_latitude,
                'longitude': tracking.current_longitude,
                'timestamp': tracking.updated_at
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['patch'])
    def update_status(self, request, pk=None):
        """Update delivery status"""
        tracking = self.get_object()
        new_status = request.data.get('status')
        notes = request.data.get('notes', '')
        
        if new_status not in dict(DeliveryTracking.STATUS_CHOICES):
            return Response(
                {'error': 'Invalid status'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        old_status = tracking.status
        tracking.status = new_status
        
        # Update timestamps based on status
        if new_status == 'picked_up' and not tracking.picked_up_at:
            tracking.picked_up_at = timezone.now()
        
        tracking.save()
        
        # Create status history
        DeliveryStatusHistory.objects.create(
            tracking=tracking,
            status=new_status,
            notes=notes,
            changed_by=request.user
        )
        
        # Update order status
        if new_status == 'delivered':
            tracking.order.status = 'delivered'
            tracking.order.actual_delivery_date = timezone.now().date()
            tracking.order.save()
        
        return Response({
            'message': f'Status updated from {old_status} to {new_status}',
            'status': tracking.status,
            'timestamp': tracking.updated_at
        })
    
    @action(detail=True, methods=['post'])
    def mark_picked_up(self, request, pk=None):
        """Mark delivery as picked up"""
        tracking = self.get_object()
        
        if tracking.status != 'assigned':
            return Response(
                {'error': 'Can only mark assigned deliveries as picked up'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        tracking.mark_picked_up()
        
        # Create status history
        DeliveryStatusHistory.objects.create(
            tracking=tracking,
            status='picked_up',
            notes='Order picked up by driver',
            changed_by=request.user
        )
        
        return Response({
            'message': 'Delivery marked as picked up',
            'status': tracking.status,
            'picked_up_at': tracking.picked_up_at
        })
    
    @action(detail=True, methods=['post'])
    def mark_delivered(self, request, pk=None):
        """Mark delivery as delivered with proof"""
        tracking = self.get_object()
        serializer = DeliveryProofSerializer(data=request.data)
        
        if serializer.is_valid():
            tracking.mark_delivered(
                notes=serializer.validated_data.get('notes', ''),
                photo=serializer.validated_data.get('proof_photo'),
                signature=serializer.validated_data.get('signature')
            )
            
            # Create status history
            DeliveryStatusHistory.objects.create(
                tracking=tracking,
                status='delivered',
                notes='Order delivered successfully',
                changed_by=request.user
            )
            
            return Response({
                'message': 'Delivery marked as delivered',
                'status': tracking.status,
                'delivered_at': tracking.delivered_at
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def submit_feedback(self, request, pk=None):
        """Submit customer feedback for delivery"""
        tracking = self.get_object()
        
        # Only allow feedback for delivered orders
        if tracking.status != 'delivered':
            return Response(
                {'error': 'Can only submit feedback for delivered orders'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Only allow customer to submit feedback
        if tracking.order.customer != request.user:
            return Response(
                {'error': 'Only the customer can submit feedback'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = CustomerFeedbackSerializer(data=request.data)
        
        if serializer.is_valid():
            tracking.customer_rating = serializer.validated_data['rating']
            tracking.customer_feedback = serializer.validated_data.get('feedback', '')
            tracking.save()
            
            # Update driver's average rating
            if tracking.driver:
                from django.db.models import Avg
                avg_rating = DeliveryTracking.objects.filter(
                    driver=tracking.driver,
                    customer_rating__isnull=False
                ).aggregate(avg=Avg('customer_rating'))['avg']
                
                tracking.driver.average_rating = avg_rating or 0
                tracking.driver.save()
            
            return Response({
                'message': 'Feedback submitted successfully',
                'rating': tracking.customer_rating,
                'feedback': tracking.customer_feedback
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['get'])
    def route_history(self, request, pk=None):
        """Get delivery route history"""
        tracking = self.get_object()
        route_points = tracking.route_points.all()
        serializer = DeliveryRouteSerializer(route_points, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def status_history(self, request, pk=None):
        """Get delivery status change history"""
        tracking = self.get_object()
        history = tracking.status_history.all()
        serializer = DeliveryStatusHistorySerializer(history, many=True)
        return Response(serializer.data)
