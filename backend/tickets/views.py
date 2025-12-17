from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import get_object_or_404
from django.db.models import Q, Count
from django.utils import timezone
from .models import Ticket, TicketComment, TicketHistory
from .serializers import (
    TicketSerializer,
    TicketListSerializer,
    CreateTicketSerializer,
    TicketCommentSerializer,
    AddCommentSerializer,
    UpdateTicketStatusSerializer,
    UpdateTicketPrioritySerializer
)
from .email_service import TicketEmailService


class TicketPagination(PageNumberPagination):
    """Custom pagination for ticket lists"""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class TicketListCreateView(APIView):
    """
    GET /api/tickets/ - List tickets with filtering
    POST /api/tickets/ - Create a new ticket
    
    Query params for GET:
    - status: filter by status (open, in_progress, resolved, closed)
    - priority: filter by priority (low, medium, high, urgent)
    - category: filter by category
    - search: search in subject and description
    """
    permission_classes = [IsAuthenticated]
    pagination_class = TicketPagination
    
    def get(self, request):
        """List tickets with filtering and pagination"""
        user = request.user
        
        # Base queryset
        if user.is_staff:
            # Staff can see all tickets
            queryset = Ticket.objects.all()
        else:
            # Customers see only their tickets
            queryset = Ticket.objects.filter(customer=user)
        
        # Apply filters
        ticket_status = request.query_params.get('status')
        if ticket_status:
            queryset = queryset.filter(status=ticket_status)
        
        priority = request.query_params.get('priority')
        if priority:
            queryset = queryset.filter(priority=priority)
        
        category = request.query_params.get('category')
        if category:
            queryset = queryset.filter(category=category)
        
        search_query = request.query_params.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(subject__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(ticket_number__icontains=search_query)
            )
        
        # Order by most recent
        queryset = queryset.order_by('-created_at')
        
        # Select related data to optimize queries
        queryset = queryset.select_related('customer', 'order')
        
        # Paginate
        paginator = self.pagination_class()
        paginated_queryset = paginator.paginate_queryset(queryset, request)
        
        # Serialize
        serializer = TicketListSerializer(paginated_queryset, many=True)
        
        # Return paginated response
        return paginator.get_paginated_response(serializer.data)
    
    def post(self, request):
        """Create a new support ticket"""
        serializer = CreateTicketSerializer(
            data=request.data,
            context={'request': request}
        )
        
        if serializer.is_valid():
            ticket = serializer.save()
            
            # Send confirmation email
            email_service = TicketEmailService()
            email_service.send_ticket_created_email(ticket)
            
            # Return full ticket details
            response_serializer = TicketSerializer(ticket)
            return Response(
                response_serializer.data,
                status=status.HTTP_201_CREATED
            )
        
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class TicketDetailView(APIView):
    """
    GET /api/tickets/{id}/
    Get detailed ticket information with comments and history
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, ticket_id):
        user = request.user
        
        # Get ticket
        ticket = get_object_or_404(Ticket, id=ticket_id)
        
        # Check permissions
        if not user.is_staff and ticket.customer != user:
            return Response(
                {'error': 'You do not have permission to view this ticket'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = TicketSerializer(ticket)
        return Response(serializer.data)


class AddCommentView(APIView):
    """
    POST /api/tickets/{id}/comments/
    Add a comment to a ticket
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request, ticket_id):
        user = request.user
        
        # Get ticket
        ticket = get_object_or_404(Ticket, id=ticket_id)
        
        # Check permissions
        if not user.is_staff and ticket.customer != user:
            return Response(
                {'error': 'You do not have permission to comment on this ticket'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Check if ticket is closed
        if ticket.status == 'closed':
            return Response(
                {'error': 'Cannot add comments to closed tickets'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate comment
        serializer = AddCommentSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create comment
        comment = TicketComment.objects.create(
            ticket=ticket,
            author=user,
            comment=serializer.validated_data['comment'],
            is_staff_comment=user.is_staff
        )
        
        # Update ticket's updated_at
        ticket.updated_at = timezone.now()
        ticket.save()
        
        # Send email notification
        email_service = TicketEmailService()
        email_service.send_comment_added_email(ticket, comment)
        
        # Return comment
        response_serializer = TicketCommentSerializer(comment)
        return Response(
            response_serializer.data,
            status=status.HTTP_201_CREATED
        )


class UpdateTicketStatusView(APIView):
    """
    PATCH /api/tickets/{id}/status/
    Update ticket status (staff only)
    """
    permission_classes = [IsAuthenticated]
    
    def patch(self, request, ticket_id):
        user = request.user
        
        # Only staff can update status
        if not user.is_staff:
            return Response(
                {'error': 'Only staff can update ticket status'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Get ticket
        ticket = get_object_or_404(Ticket, id=ticket_id)
        
        # Validate status change
        serializer = UpdateTicketStatusSerializer(
            data=request.data,
            context={'ticket': ticket}
        )
        
        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get old values
        old_status = ticket.status
        new_status = serializer.validated_data['status']
        reason = serializer.validated_data.get('reason', '')
        
        # Update status
        ticket.status = new_status
        
        # Update timestamps based on status
        if new_status == 'resolved' and old_status != 'resolved':
            ticket.resolved_at = timezone.now()
        elif new_status == 'closed' and old_status != 'closed':
            ticket.closed_at = timezone.now()
        
        ticket.save()
        
        # Create history entry
        TicketHistory.objects.create(
            ticket=ticket,
            changed_by=user,
            field_changed='status',
            old_value=old_status,
            new_value=new_status,
            change_reason=reason
        )
        
        # Send appropriate email notifications
        email_service = TicketEmailService()
        if new_status == 'resolved':
            email_service.send_ticket_resolved_email(ticket)
        elif new_status == 'closed':
            email_service.send_ticket_closed_email(ticket)
        else:
            email_service.send_status_updated_email(ticket, old_status, new_status)
        
        # Return updated ticket
        response_serializer = TicketSerializer(ticket)
        return Response(response_serializer.data)


class UpdateTicketPriorityView(APIView):
    """
    PATCH /api/tickets/{id}/priority/
    Update ticket priority (staff only)
    """
    permission_classes = [IsAuthenticated]
    
    def patch(self, request, ticket_id):
        user = request.user
        
        # Only staff can update priority
        if not user.is_staff:
            return Response(
                {'error': 'Only staff can update ticket priority'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Get ticket
        ticket = get_object_or_404(Ticket, id=ticket_id)
        
        # Validate priority change
        serializer = UpdateTicketPrioritySerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get old values
        old_priority = ticket.priority
        new_priority = serializer.validated_data['priority']
        reason = serializer.validated_data.get('reason', '')
        
        # Update priority
        ticket.priority = new_priority
        ticket.save()
        
        # Create history entry
        TicketHistory.objects.create(
            ticket=ticket,
            changed_by=user,
            field_changed='priority',
            old_value=old_priority,
            new_value=new_priority,
            change_reason=reason
        )
        
        # Return updated ticket
        response_serializer = TicketSerializer(ticket)
        return Response(response_serializer.data)


class TicketStatsView(APIView):
    """
    GET /api/tickets/stats/
    Get ticket statistics (staff only)
    Returns counts by status, priority, and category
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user
        
        # Only staff can view stats
        if not user.is_staff:
            return Response(
                {'error': 'Only staff can view ticket statistics'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Get counts by status
        status_counts = {}
        for status_choice, _ in Ticket.STATUS_CHOICES:
            count = Ticket.objects.filter(status=status_choice).count()
            status_counts[status_choice] = count
        
        # Get counts by priority
        priority_counts = {}
        for priority_choice, _ in Ticket.PRIORITY_CHOICES:
            count = Ticket.objects.filter(priority=priority_choice).count()
            priority_counts[priority_choice] = count
        
        # Get counts by category
        category_counts = {}
        for category_choice, _ in Ticket.CATEGORY_CHOICES:
            count = Ticket.objects.filter(category=category_choice).count()
            category_counts[category_choice] = count
        
        # Get total counts
        total_tickets = Ticket.objects.count()
        open_tickets = Ticket.objects.filter(
            status__in=['open', 'in_progress']
        ).count()
        
        # Get recent activity (last 7 days)
        from datetime import timedelta
        seven_days_ago = timezone.now() - timedelta(days=7)
        recent_tickets = Ticket.objects.filter(
            created_at__gte=seven_days_ago
        ).count()
        
        return Response({
            'total_tickets': total_tickets,
            'open_tickets': open_tickets,
            'recent_tickets': recent_tickets,
            'by_status': status_counts,
            'by_priority': priority_counts,
            'by_category': category_counts
        })
