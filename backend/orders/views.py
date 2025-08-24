from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.utils import timezone
from datetime import date, datetime
from django.db.models import Q
from django.core.paginator import Paginator

from .models import Order, OrderItem
from .serializers import (
    OrderSerializer, OrderItemSerializer, CreateOrderSerializer,
    OrderStatusUpdateSerializer, OrderSummarySerializer
)
from .utils import CSVGenerator
from .email_service import EmailService
from .order_processor import OrderProcessor
from cart.models import Cart
from products.models import Product

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_order(request):
    """Create a new order from user's cart"""
    try:
        # Get user's active cart
        cart = Cart.objects.filter(user=request.user, is_active=True).first()
        if not cart or not cart.items.exists():
            return Response(
                {'error': 'No active cart or cart is empty'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate order data
        serializer = CreateOrderSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        with transaction.atomic():
            # Create order
            order_data = serializer.validated_data
            order = Order.objects.create(
                customer=request.user,
                delivery_address=order_data['delivery_address'],
                delivery_instructions=order_data.get('delivery_instructions', ''),
                preferred_delivery_date=order_data.get('preferred_delivery_date'),
                business_name=order_data['business_name'],
                contact_person=order_data['contact_person'],
                phone_number=order_data['phone_number']
            )
            
            # Create order items from cart
            total_items = 0
            for cart_item in cart.items.all():
                OrderItem.objects.create(
                    order=order,
                    product=cart_item.product,
                    quantity=cart_item.quantity
                )
                total_items += cart_item.quantity
            
            # Update order total
            order.total_items = total_items
            order.save()
            
            # Clear the cart
            cart.clear()
            cart.is_active = False
            cart.save()
            
            # Send email notifications
            try:
                email_service = EmailService()
                
                # Send order confirmation to customer
                email_service.send_order_confirmation_email(
                    order, request.user.email
                )
                
                # Send notification to delivery coordinator
                email_service.send_delivery_coordinator_notification(order)
                
            except Exception as email_error:
                # Log email error but don't fail the order creation
                print(f"Email notification failed: {str(email_error)}")
            
            # Return created order
            order_serializer = OrderSerializer(order)
            return Response({
                'message': 'Order created successfully',
                'order': order_serializer.data
            }, status=status.HTTP_201_CREATED)
            
    except Exception as e:
        return Response(
            {'error': f'Failed to create order: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_order(request, order_id):
    """Get detailed order information"""
    try:
        order = get_object_or_404(Order, id=order_id, customer=request.user)
        serializer = OrderSerializer(order)
        return Response(serializer.data)
    except Order.DoesNotExist:
        return Response(
            {'error': 'Order not found'},
            status=status.HTTP_404_NOT_FOUND
        )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_orders(request):
    """Get user's order history with pagination"""
    try:
        # Get query parameters
        page = int(request.GET.get('page', 1))
        page_size = int(request.GET.get('page_size', 10))
        status_filter = request.GET.get('status', '')
        
        # Filter orders
        orders = Order.objects.filter(customer=request.user)
        if status_filter:
            orders = orders.filter(status=status_filter)
        
        # Pagination
        start = (page - 1) * page_size
        end = start + page_size
        paginated_orders = orders[start:end]
        
        # Serialize orders
        serializer = OrderSummarySerializer(paginated_orders, many=True)
        
        return Response({
            'orders': serializer.data,
            'pagination': {
                'page': page,
                'page_size': page_size,
                'total_orders': orders.count(),
                'total_pages': (orders.count() + page_size - 1) // page_size
            }
        })
        
    except Exception as e:
        return Response(
            {'error': f'Failed to retrieve orders: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def update_order_status(request, order_id):
    """Update order status (admin/staff only)"""
    try:
        order = get_object_or_404(Order, id=order_id)
        
        # Check if user can update status (admin or staff)
        if not request.user.is_staff:
            return Response(
                {'error': 'Permission denied'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = OrderStatusUpdateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        new_status = serializer.validated_data['status']
        old_status = order.status
        
        # Get additional data for processing
        notes = request.data.get('notes', '')
        user = request.user.username
        
        # Use OrderProcessor for automated workflow
        order_processor = OrderProcessor()
        success = order_processor.process_order_status_change(
            order=order,
            new_status=new_status,
            old_status=old_status,
            notes=notes,
            user=user
        )
        
        if success:
            return Response({
                'message': f'Order status updated to {order.get_status_display()}',
                'order': OrderSerializer(order).data,
                'automated_processing': 'completed'
            })
        else:
            return Response({
                'message': f'Order status updated to {order.get_status_display()}',
                'order': OrderSerializer(order).data,
                'warning': 'Automated processing failed, but status was updated'
            })
        
    except Exception as e:
        return Response(
            {'error': f'Failed to update order status: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def cancel_order(request, order_id):
    """Cancel an order"""
    try:
        order = get_object_or_404(Order, id=order_id, customer=request.user)
        
        if not order.can_be_cancelled():
            return Response(
                {'error': 'Order cannot be cancelled at this stage'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        old_status = order.status
        
        # Use OrderProcessor for automated workflow
        order_processor = OrderProcessor()
        notes = request.data.get('cancellation_reason', 'Cancelled by customer')
        
        success = order_processor.process_order_status_change(
            order=order,
            new_status='cancelled',
            old_status=old_status,
            notes=notes,
            user=request.user.username
        )
        
        if success:
            return Response({
                'message': 'Order cancelled successfully',
                'order': OrderSerializer(order).data,
                'automated_processing': 'completed'
            })
        else:
            return Response({
                'message': 'Order cancelled successfully',
                'order': OrderSerializer(order).data,
                'warning': 'Automated processing failed, but order was cancelled'
            })
        
    except Exception as e:
        return Response(
            {'error': f'Failed to cancel order: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def order_stats(request):
    """Get order statistics for the user"""
    try:
        user_orders = Order.objects.filter(customer=request.user)
        
        stats = {
            'total_orders': user_orders.count(),
            'pending_orders': user_orders.filter(status='pending').count(),
            'confirmed_orders': user_orders.filter(status='confirmed').count(),
            'processing_orders': user_orders.filter(status='processing').count(),
            'ready_orders': user_orders.filter(status='ready').count(),
            'delivered_orders': user_orders.filter(status='delivered').count(),
            'cancelled_orders': user_orders.filter(status='cancelled').count(),
            'total_items_ordered': sum(order.total_items for order in user_orders),
        }
        
        return Response(stats)
        
    except Exception as e:
        return Response(
            {'error': f'Failed to retrieve order stats: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def download_order_csv(request, order_id):
    """Download CSV for a specific order"""
    try:
        order = get_object_or_404(Order, id=order_id, customer=request.user)
        
        # Generate CSV content
        csv_content = CSVGenerator.generate_order_csv(order)
        filename = CSVGenerator.generate_order_csv_filename(order)
        
        # Create HTTP response with CSV content
        from django.http import HttpResponse
        response = HttpResponse(csv_content, content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        return response
        
    except Exception as e:
        return Response(
            {'error': f'Failed to generate CSV: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def download_orders_summary_csv(request):
    """Download CSV summary of user's orders"""
    try:
        # Get user's orders
        user_orders = Order.objects.filter(customer=request.user).order_by('-created_at')
        
        if not user_orders.exists():
            return Response(
                {'error': 'No orders found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Generate CSV content
        csv_content = CSVGenerator.generate_orders_summary_csv(user_orders)
        filename = f"DesiDeliver_OrdersSummary_{request.user.username}_{datetime.now().strftime('%Y%m%d')}.csv"
        
        # Create HTTP response with CSV content
        from django.http import HttpResponse
        response = HttpResponse(csv_content, content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        return response
        
    except Exception as e:
        return Response(
            {'error': f'Failed to generate CSV: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def download_daily_orders_csv(request):
    """Download CSV for all orders on a specific date (admin/staff only)"""
    try:
        # Check if user can access daily orders (admin or staff)
        if not request.user.is_staff:
            return Response(
                {'error': 'Permission denied'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Get date parameter
        date_str = request.GET.get('date')
        if not date_str:
            # Default to today
            target_date = datetime.now().date()
        else:
            try:
                target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            except ValueError:
                return Response(
                    {'error': 'Invalid date format. Use YYYY-MM-DD'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Get orders for the date
        orders = Order.objects.filter(created_at__date=target_date)
        
        if not orders.exists():
            return Response(
                {'error': f'No orders found for {target_date}'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Generate CSV content
        csv_content = CSVGenerator.generate_daily_orders_csv(orders, target_date)
        filename = CSVGenerator.generate_daily_orders_filename(target_date)
        
        # Create HTTP response with CSV content
        from django.http import HttpResponse
        response = HttpResponse(csv_content, content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        return response
        
    except Exception as e:
        return Response(
            {'error': f'Failed to generate CSV: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_daily_summary_email(request):
    """Send daily orders summary email to delivery coordinator"""
    try:
        # Check if user can send daily summary (admin or staff)
        if not request.user.is_staff:
            return Response(
                {'error': 'Permission denied'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Get date from request, default to today
        date_str = request.data.get('date', timezone.now().date().isoformat())
        
        try:
            target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return Response(
                {'error': 'Invalid date format. Use YYYY-MM-DD'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get orders for the specified date
        orders = Order.objects.filter(
            created_at__date=target_date
        ).order_by('created_at')
        
        if not orders.exists():
            return Response(
                {'error': f'No orders found for {date_str}'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Send daily summary email
        email_service = EmailService()
        date_formatted = target_date.strftime('%B %d, %Y')
        
        success = email_service.send_daily_orders_summary(orders, date_formatted)
        
        if success:
            return Response({
                'message': f'Daily summary email sent successfully for {date_formatted}',
                'orders_count': orders.count()
            }, status=status.HTTP_200_OK)
        else:
            return Response(
                {'error': 'Failed to send daily summary email'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
    except Exception as e:
        return Response(
            {'error': f'Failed to send daily summary email: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def bulk_process_orders(request):
    """Bulk process multiple orders (admin/staff only)"""
    try:
        # Check if user can bulk process orders
        if not request.user.is_staff:
            return Response(
                {'error': 'Permission denied'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Get orders to process
        order_ids = request.data.get('order_ids', [])
        action = request.data.get('action', '')  # 'confirm', 'process', 'ready', 'deliver'
        notes = request.data.get('notes', '')
        
        if not order_ids:
            return Response(
                {'error': 'No order IDs provided'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not action:
            return Response(
                {'error': 'No action specified'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Map actions to statuses
        action_to_status = {
            'confirm': 'confirmed',
            'process': 'processing',
            'ready': 'ready',
            'deliver': 'delivered'
        }
        
        if action not in action_to_status:
            return Response(
                {'error': f'Invalid action: {action}. Valid actions: {list(action_to_status.keys())}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        new_status = action_to_status[action]
        processed_orders = []
        failed_orders = []
        
        # Process each order
        order_processor = OrderProcessor()
        for order_id in order_ids:
            try:
                order = Order.objects.get(id=order_id)
                old_status = order.status
                
                success = order_processor.process_order_status_change(
                    order=order,
                    new_status=new_status,
                    old_status=old_status,
                    notes=notes,
                    user=request.user.username
                )
                
                if success:
                    processed_orders.append({
                        'order_id': order_id,
                        'order_number': order.order_number,
                        'status': 'success'
                    })
                else:
                    failed_orders.append({
                        'order_id': order_id,
                        'order_number': order.order_number,
                        'status': 'failed'
                    })
                    
            except Order.DoesNotExist:
                failed_orders.append({
                    'order_id': order_id,
                    'order_number': 'N/A',
                    'status': 'not_found'
                })
            except Exception as e:
                failed_orders.append({
                    'order_id': order_id,
                    'order_number': 'N/A',
                    'status': 'error',
                    'error': str(e)
                })
        
        return Response({
            'message': f'Bulk processing completed for {len(processed_orders)} orders',
            'action': action,
            'new_status': new_status,
            'processed_orders': processed_orders,
            'failed_orders': failed_orders,
            'summary': {
                'total_requested': len(order_ids),
                'successful': len(processed_orders),
                'failed': len(failed_orders)
            }
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {'error': f'Failed to bulk process orders: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_orders_for_staff(request):
    """Get orders for staff management (admin/staff only)"""
    try:
        # Check if user can access staff orders
        if not request.user.is_staff:
            return Response(
                {'error': 'Permission denied'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Get query parameters
        status_filter = request.GET.get('status', '')
        date_filter = request.GET.get('date', '')
        search_query = request.GET.get('search', '')
        page = int(request.GET.get('page', 1))
        page_size = int(request.GET.get('page_size', 20))
        
        # Build queryset
        orders = Order.objects.all()
        
        # Apply filters
        if status_filter:
            orders = orders.filter(status=status_filter)
        
        if date_filter:
            try:
                from datetime import datetime
                target_date = datetime.strptime(date_filter, '%Y-%m-%d').date()
                orders = orders.filter(created_at__date=target_date)
            except ValueError:
                pass
        
        if search_query:
            # Enhanced search with multiple strategies
            search_terms = search_query.strip().split()
            search_filters = Q()
            
            for term in search_terms:
                if term:  # Skip empty terms
                    # Create a filter for each search term
                    term_filter = (
                        Q(order_number__icontains=term) |
                        Q(business_name__icontains=term) |
                        Q(contact_person__icontains=term) |
                        Q(phone_number__icontains=term) |
                        Q(delivery_address__icontains=term) |
                        Q(delivery_instructions__icontains=term) |
                        Q(status__icontains=term) |
                        Q(customer__username__icontains=term) |
                        Q(customer__email__icontains=term) |
                        Q(customer__first_name__icontains=term) |
                        Q(customer__last_name__icontains=term) |
                        Q(customer__business_name__icontains=term)
                    )
                    
                    # Add to main search filter (AND logic between terms)
                    search_filters &= term_filter
            
            # Apply the search filter
            orders = orders.filter(search_filters)
        
        # Order by priority (pending first, then by creation date)
        from django.db.models import Case, When, Value, IntegerField
        orders = orders.annotate(
            priority=Case(
                When(status='pending', then=Value(1)),
                When(status='confirmed', then=Value(2)),
                When(status='processing', then=Value(3)),
                When(status='ready', then=Value(4)),
                When(status='delivered', then=Value(5)),
                When(status='cancelled', then=Value(6)),
                default=Value(7),
                output_field=IntegerField(),
            )
        ).order_by('priority', '-created_at')
        
        # Pagination
        paginator = Paginator(orders, page_size)
        page_obj = paginator.get_page(page)
        
        # Prepare response data
        orders_data = []
        for order in page_obj:
            order_data = {
                'id': order.id,
                'order_number': order.order_number,
                'status': order.status,
                'status_display': order.get_status_display(),
                'business_name': order.business_name,
                'contact_person': order.contact_person,
                'phone_number': order.phone_number,
                'delivery_address': order.delivery_address,
                'total_items': order.total_items,
                'created_at': order.created_at,
                'updated_at': order.updated_at,
                'preferred_delivery_date': order.preferred_delivery_date,
                'delivery_instructions': order.delivery_instructions,
                'can_be_updated': order.status not in ['delivered', 'cancelled'],
                'next_available_statuses': get_next_available_statuses(order.status)
            }
            orders_data.append(order_data)
        
        return Response({
            'orders': orders_data,
            'pagination': {
                'page': page,
                'page_size': page_size,
                'total_pages': paginator.num_pages,
                'total_orders': paginator.count,
                'has_next': page_obj.has_next(),
                'has_previous': page_obj.has_previous(),
            },
            'filters': {
                'status_filter': status_filter,
                'date_filter': date_filter,
                'search_query': search_query,
            },
            'summary': {
                'total_orders': orders.count(),
                'pending_orders': orders.filter(status='pending').count(),
                'confirmed_orders': orders.filter(status='confirmed').count(),
                'processing_orders': orders.filter(status='processing').count(),
                'ready_orders': orders.filter(status='ready').count(),
                'delivered_orders': orders.filter(status='delivered').count(),
                'cancelled_orders': orders.filter(status='cancelled').count(),
            }
        })
        
    except Exception as e:
        return Response(
            {'error': f'Failed to retrieve orders for staff: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

def get_next_available_statuses(current_status):
    """Get next available statuses based on current status"""
    status_flow = {
        'pending': ['confirmed', 'cancelled'],
        'confirmed': ['processing', 'cancelled'],
        'processing': ['ready', 'cancelled'],
        'ready': ['delivered', 'cancelled'],
        'delivered': [],  # Final status
        'cancelled': [],  # Final status
    }
    return status_flow.get(current_status, [])
