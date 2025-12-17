from django.urls import path
from .views import (
    TicketListCreateView,
    TicketDetailView,
    AddCommentView,
    UpdateTicketStatusView,
    UpdateTicketPriorityView,
    TicketStatsView
)

app_name = 'tickets'

urlpatterns = [
    # Ticket CRUD (combined list + create)
    path('', TicketListCreateView.as_view(), name='tickets'),  # GET & POST
    path('stats/', TicketStatsView.as_view(), name='ticket_stats'),  # GET
    path('<int:ticket_id>/', TicketDetailView.as_view(), name='ticket_detail'),  # GET
    
    # Ticket actions
    path('<int:ticket_id>/comments/', AddCommentView.as_view(), name='add_comment'),  # POST
    path('<int:ticket_id>/status/', UpdateTicketStatusView.as_view(), name='update_status'),  # PATCH
    path('<int:ticket_id>/priority/', UpdateTicketPriorityView.as_view(), name='update_priority'),  # PATCH
]
