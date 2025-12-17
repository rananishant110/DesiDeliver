# Product Requirements Document: Customer Support Ticketing System

## Title
Customer Support Ticketing System - Order Issues & Customer Support Management

## Overview
A comprehensive ticketing system that enables DesiDeliver customers (restaurant/store owners) to raise complaints, concerns, and inquiries about their orders or account. Staff members can view, respond to, and manage tickets through a dedicated support dashboard with status tracking and email notifications.

## Problem Statement
Currently, DesiDeliver customers have no structured way to report issues with their orders or seek support. Communication happens through phone calls or emails, which are:
- Difficult to track and manage
- Lack proper status visibility
- No historical record for reference
- Time-consuming for both customers and support staff
- No priority management for urgent issues

This ticketing system will provide a centralized, trackable, and efficient support channel.

## User Stories

### As a Restaurant/Store Owner (Customer)
- I want to create a support ticket for my order issue so that I can get help
- I want to view all my past and current tickets so that I can track their status
- I want to add comments to my tickets so that I can provide additional information
- I want to receive email notifications when staff responds so that I stay updated
- I want to see the history of my ticket so that I know what actions were taken
- I want to create general inquiry tickets even without an order so that I can get support

### As a Delivery Coordinator/Admin (Staff)
- I want to view all customer tickets so that I can prioritize support work
- I want to filter tickets by status, priority, and category so that I can focus on urgent issues
- I want to change ticket status so that customers know progress is being made
- I want to add comments to tickets so that I can communicate with customers
- I want to link tickets to specific orders so that I can review order details
- I want to see ticket history so that I can understand the complete context
- I want customers to receive email notifications so that they stay informed

### As a System Administrator
- I want to track support metrics so that I can improve customer service
- I want to ensure all tickets are resolved in a timely manner
- I want to monitor ticket volume and categories to identify systemic issues

## Functional Requirements

### 1. Ticket Creation
- Customers can create tickets from their dashboard
- Required fields: subject, description, category, priority (optional - defaults to medium)
- Optional fields: related order (dropdown of customer's orders), priority override
- Categories: Order Issue, Product Quality, Delivery Problem, Payment Issue, Account Support, General Inquiry
- Priority levels: Low, Medium, High, Urgent
- Auto-assign ticket number (format: TKT{YYYYMMDD}{###})
- Initial status: "open"
- Timestamp tracking: created_at, updated_at

### 2. Ticket Viewing & Listing
- **Customers**: View only their own tickets
- **Staff**: View all tickets from all customers
- List view displays: ticket number, subject, status, priority, category, created date, last updated
- Sorting: by date (newest first), priority, status
- Filtering: by status, priority, category, date range
- Pagination: 20 tickets per page
- Search: by ticket number, subject, order number

### 3. Ticket Detail View
- Display complete ticket information:
  - Ticket number, status, priority, category
  - Customer details (name, business, contact)
  - Related order (if linked) with link to order details
  - Subject and description
  - Creation and last update timestamps
  - Status history (who changed status, when, and why)
- Comment thread showing all communications
- Action buttons based on user role

### 4. Comments & Communication
- Both customers and staff can add comments
- Comments display: author name, timestamp, comment text
- Comments are chronologically ordered (oldest first)
- Staff comments are distinguished visually
- Character limit: 2000 characters per comment
- Email notification sent when new comment is added

### 5. Status Management
- Status workflow: open → in_progress → resolved → closed
- **Staff only** can change status
- Status change requires optional reason/note
- Status changes are logged in ticket history
- Email notification sent to customer on status change
- Customers cannot reopen closed tickets (must create new ticket)

### 6. Priority Management
- Default priority: Medium
- Customers can set initial priority (High/Urgent require justification)
- **Staff only** can change priority after creation
- Priority changes are logged in history
- High priority tickets highlighted in list view

### 7. Order Integration
- Tickets can optionally link to an order
- Dropdown shows customer's orders (most recent first)
- Staff can view order details from ticket page
- Order details show: order number, date, items, status
- Orders page can show if any tickets exist for that order

## Technical Requirements

### Backend Changes

#### Django App: New App "tickets"
Create new Django app for ticket management:
```bash
python manage.py startapp tickets
```

#### Models (tickets/models.py)
```python
class Ticket(models.Model):
    # Core fields
    ticket_number = models.CharField(max_length=20, unique=True)
    customer = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='tickets')
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, blank=True, related_name='tickets')
    
    # Ticket details
    subject = models.CharField(max_length=200)
    description = models.TextField()
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    closed_at = models.DateTimeField(null=True, blank=True)

class TicketComment(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    comment = models.TextField(max_length=2000)
    is_staff_comment = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

class TicketHistory(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='history')
    changed_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    field_changed = models.CharField(max_length=50)
    old_value = models.CharField(max_length=200)
    new_value = models.CharField(max_length=200)
    change_reason = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
```

#### Serializers (tickets/serializers.py)
- TicketSerializer (full ticket with nested comments)
- TicketListSerializer (summary for list view)
- TicketCommentSerializer
- CreateTicketSerializer
- UpdateTicketStatusSerializer
- TicketHistorySerializer

#### Views (tickets/views.py)
- `create_ticket`: POST - Create new ticket
- `list_tickets`: GET - List tickets (filtered by user role)
- `ticket_detail`: GET - Get single ticket with comments
- `add_comment`: POST - Add comment to ticket
- `update_ticket_status`: PATCH - Update ticket status (staff only)
- `update_ticket_priority`: PATCH - Update priority (staff only)
- `ticket_stats`: GET - Get ticket statistics (staff only)

#### URLs (tickets/urls.py)
```python
/api/tickets/
  POST /create/ - Create ticket
  GET / - List tickets (with filters)
  GET /{id}/ - Get ticket details
  POST /{id}/comment/ - Add comment
  PATCH /{id}/status/ - Update status
  PATCH /{id}/priority/ - Update priority
  GET /stats/ - Get ticket stats (staff)
```

### Frontend Changes

#### TypeScript Interfaces (src/types/index.ts)
```typescript
interface Ticket {
  id: number;
  ticket_number: string;
  customer: User;
  order?: Order;
  subject: string;
  description: string;
  category: TicketCategory;
  priority: TicketPriority;
  status: TicketStatus;
  created_at: string;
  updated_at: string;
  resolved_at?: string;
  closed_at?: string;
  comments: TicketComment[];
  history: TicketHistory[];
}

type TicketCategory = 'order_issue' | 'product_quality' | 'delivery' | 'payment' | 'account' | 'general';
type TicketPriority = 'low' | 'medium' | 'high' | 'urgent';
type TicketStatus = 'open' | 'in_progress' | 'resolved' | 'closed';

interface TicketComment {
  id: number;
  author: User;
  comment: string;
  is_staff_comment: boolean;
  created_at: string;
}

interface TicketHistory {
  id: number;
  changed_by: User;
  field_changed: string;
  old_value: string;
  new_value: string;
  change_reason: string;
  created_at: string;
}

interface CreateTicketData {
  subject: string;
  description: string;
  category: TicketCategory;
  priority: TicketPriority;
  order_id?: number;
}
```

#### API Service (src/services/api.ts)
```typescript
export const ticketsAPI = {
  createTicket: (data: CreateTicketData) => api.post('/tickets/create/', data),
  getTickets: (filters?: TicketFilters) => api.get('/tickets/', { params: filters }),
  getTicket: (id: number) => api.get(`/tickets/${id}/`),
  addComment: (ticketId: number, comment: string) => api.post(`/tickets/${ticketId}/comment/`, { comment }),
  updateStatus: (ticketId: number, status: TicketStatus, reason?: string) => 
    api.patch(`/tickets/${ticketId}/status/`, { status, reason }),
  updatePriority: (ticketId: number, priority: TicketPriority) => 
    api.patch(`/tickets/${ticketId}/priority/`, { priority }),
  getTicketStats: () => api.get('/tickets/stats/'),
};
```

#### New Components (src/components/tickets/)
1. **TicketList.tsx** - List all tickets with filters
2. **TicketCard.tsx** - Individual ticket card in list
3. **TicketDetail.tsx** - Full ticket details page
4. **CreateTicketForm.tsx** - Modal form to create ticket
5. **TicketComments.tsx** - Comment thread display
6. **AddCommentForm.tsx** - Form to add new comment
7. **TicketStatusBadge.tsx** - Visual status indicator
8. **TicketFilters.tsx** - Filter controls (status, priority, category)
9. **StaffTicketDashboard.tsx** - Staff ticket management interface
10. **TicketStats.tsx** - Statistics widget for staff

#### Context Updates
Optional: Create TicketContext for managing ticket state (or use component-level state)

#### Navigation Updates
- Add "Support" menu item in customer dashboard
- Add "Tickets" menu item in staff dashboard
- Badge showing open ticket count

### Database Changes

#### New Tables
1. **tickets_ticket** - Main ticket table
2. **tickets_ticketcomment** - Comments on tickets
3. **tickets_tickethistory** - Status/priority change history

#### Indexes
- Index on ticket_number (for quick lookup)
- Index on customer_id (for filtering customer tickets)
- Index on status (for filtering)
- Index on priority (for filtering)
- Index on created_at (for sorting)
- Composite index on (status, priority) for dashboard queries

#### Relationships
- Ticket → Customer (ForeignKey to CustomUser)
- Ticket → Order (ForeignKey to Order, nullable)
- TicketComment → Ticket (ForeignKey)
- TicketComment → Author (ForeignKey to CustomUser)
- TicketHistory → Ticket (ForeignKey)
- TicketHistory → ChangedBy (ForeignKey to CustomUser)

## API Specifications

### Create Ticket
```
POST /api/tickets/create/
Authentication: JWT Required
Permissions: IsAuthenticated

Request:
{
  "subject": "Order items missing",
  "description": "My order #DD202512150001 was delivered with 2 items missing",
  "category": "order_issue",
  "priority": "high",
  "order_id": 123
}

Response (201):
{
  "id": 1,
  "ticket_number": "TKT202512150001",
  "customer": { ... },
  "order": { ... },
  "subject": "Order items missing",
  "description": "...",
  "category": "order_issue",
  "priority": "high",
  "status": "open",
  "created_at": "2025-12-15T10:30:00Z",
  "updated_at": "2025-12-15T10:30:00Z",
  "comments": [],
  "history": []
}

Errors:
400 - Invalid data
401 - Not authenticated
```

### List Tickets
```
GET /api/tickets/?status=open&priority=high&page=1
Authentication: JWT Required
Permissions: IsAuthenticated

Response (200):
{
  "count": 45,
  "next": "/api/tickets/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "ticket_number": "TKT202512150001",
      "subject": "Order items missing",
      "status": "open",
      "priority": "high",
      "category": "order_issue",
      "customer": { "id": 5, "business_name": "Taste of India" },
      "order": { "order_number": "DD202512150001" },
      "created_at": "2025-12-15T10:30:00Z",
      "updated_at": "2025-12-15T10:30:00Z"
    },
    ...
  ]
}
```

### Get Ticket Detail
```
GET /api/tickets/{id}/
Authentication: JWT Required
Permissions: IsAuthenticated (own tickets) or IsStaff (all tickets)

Response (200):
{
  "id": 1,
  "ticket_number": "TKT202512150001",
  "customer": { ... },
  "order": { ... },
  "subject": "Order items missing",
  "description": "...",
  "category": "order_issue",
  "priority": "high",
  "status": "in_progress",
  "created_at": "2025-12-15T10:30:00Z",
  "updated_at": "2025-12-15T11:45:00Z",
  "comments": [
    {
      "id": 1,
      "author": { "id": 1, "username": "staff@desideliver.com" },
      "comment": "We are looking into this issue.",
      "is_staff_comment": true,
      "created_at": "2025-12-15T11:00:00Z"
    }
  ],
  "history": [
    {
      "id": 1,
      "changed_by": { ... },
      "field_changed": "status",
      "old_value": "open",
      "new_value": "in_progress",
      "change_reason": "Assigned to support team",
      "created_at": "2025-12-15T11:00:00Z"
    }
  ]
}

Errors:
403 - Not authorized to view this ticket
404 - Ticket not found
```

### Add Comment
```
POST /api/tickets/{id}/comment/
Authentication: JWT Required
Permissions: IsAuthenticated (own tickets) or IsStaff (all tickets)

Request:
{
  "comment": "I also noticed that the rice quality was poor"
}

Response (201):
{
  "id": 2,
  "author": { "id": 5, "business_name": "Taste of India" },
  "comment": "I also noticed that the rice quality was poor",
  "is_staff_comment": false,
  "created_at": "2025-12-15T12:00:00Z"
}
```

### Update Status
```
PATCH /api/tickets/{id}/status/
Authentication: JWT Required
Permissions: IsStaff

Request:
{
  "status": "resolved",
  "reason": "Issue has been addressed and replacement items sent"
}

Response (200):
{
  "id": 1,
  "status": "resolved",
  "updated_at": "2025-12-15T14:00:00Z"
}

Errors:
403 - Only staff can update status
400 - Invalid status transition
```

## UI/UX Requirements

### Material-UI Components
- **Card** - Ticket cards in list view
- **Chip** - Status and priority badges
- **TextField** - Subject, description, comment input
- **Select** - Category, priority, order selection
- **Button** - Create ticket, add comment, status actions
- **Dialog** - Create ticket modal
- **Tabs** - Filter tickets by status
- **Badge** - Notification count on support menu
- **Timeline** - Display ticket history
- **Accordion** - Comments section
- **Alert** - Success/error messages

### Customer User Flow
1. Navigate to Dashboard → Click "Support" menu
2. See list of their tickets with status badges
3. Click "Create Ticket" button → Modal opens
4. Fill form: subject, description, category, priority, order (optional)
5. Submit → Success message → Ticket appears in list
6. Click ticket card → View detail page
7. See all comments and history
8. Add comment → Comment appears immediately
9. Receive email when staff responds

### Staff User Flow
1. Navigate to Staff Dashboard → Click "Tickets" menu
2. See all tickets from all customers
3. Use filters: status (tabs), priority (dropdown), category (dropdown)
4. High priority tickets highlighted with red border
5. Click ticket → View detail with customer and order info
6. Read customer description and comments
7. Add staff comment → Customer receives email
8. Change status → Select new status, add reason → Customer receives email
9. View statistics widget: open tickets, avg resolution time

### Form Validation Rules
- Subject: Required, 5-200 characters
- Description: Required, 20-2000 characters
- Category: Required, must be valid option
- Priority: Optional, defaults to medium
- Order: Optional, must be customer's own order
- Comment: Required when adding comment, 1-2000 characters
- Status reason: Optional but recommended when changing status

### Error Handling
- Show inline validation errors on form fields
- Display API error messages in Alert component
- Show loading spinners during API calls
- Disable submit button while processing
- Show success snackbar after successful actions

### Loading States
- Skeleton loaders for ticket list while loading
- Progress indicator on buttons during submission
- Disabled state for forms during processing

### Mobile Responsiveness
- Stack ticket cards vertically on mobile
- Full-width forms on small screens
- Collapsible filters on mobile
- Touch-friendly buttons and inputs

## Email Notifications

### Customer Notifications
1. **Ticket Created** - Confirmation email with ticket number
2. **Staff Responded** - Email when staff adds comment
3. **Status Changed** - Email when ticket status updates
4. **Ticket Resolved** - Email when marked resolved

### Staff Notifications
1. **New Ticket Created** - Email to support team
2. **Customer Responded** - Email when customer adds comment
3. **High Priority Ticket** - Immediate email for urgent tickets

### Email Template Structure
```html
Subject: [DesiDeliver] Ticket #{ticket_number} - {action}

Dear {customer_name},

Your support ticket #{ticket_number} regarding "{subject}" has been {action}.

Status: {status}
Priority: {priority}

{additional_message}

View ticket: {ticket_url}

Best regards,
DesiDeliver Support Team
```

## Success Criteria

### Functional Acceptance Criteria
- [ ] Customers can create tickets with all required fields
- [ ] Tickets are automatically assigned unique ticket numbers
- [ ] Customers can only view their own tickets
- [ ] Staff can view all tickets from all customers
- [ ] Comments can be added by both customers and staff
- [ ] Staff can update ticket status
- [ ] Status changes are logged in history
- [ ] Email notifications are sent on ticket creation, comments, and status changes
- [ ] Tickets can be filtered by status, priority, and category
- [ ] Tickets can be linked to orders
- [ ] Ticket list shows pagination
- [ ] Search functionality works for ticket numbers and subjects

### Performance Requirements
- Ticket list loads in under 2 seconds
- Ticket detail page loads in under 1 second
- Comment submission completes in under 500ms
- Email notifications sent within 30 seconds

### User Experience Goals
- 95% of customers can create tickets without assistance
- Average ticket response time under 2 hours during business hours
- Customer satisfaction rating 4.5+ for support experience

## Security Considerations

### Authentication
- All ticket endpoints require JWT authentication
- Customers can only access their own tickets
- Staff authentication required for admin actions

### Authorization
- Customers can create, view own tickets, add comments to own tickets
- Staff can view all tickets, add comments to all tickets, change status/priority
- Prevent customers from changing ticket status
- Prevent customers from viewing other customers' tickets

### Input Validation
- Sanitize all text inputs to prevent XSS
- Validate category, priority, status against allowed values
- Ensure order_id belongs to the customer creating ticket
- Limit comment length to prevent abuse
- Rate limiting on ticket creation (max 10 per hour per customer)

### Data Protection
- Ticket data includes sensitive customer information
- Log all ticket accesses for audit trail
- Ensure proper foreign key constraints prevent orphaned records

## Constraints & Assumptions

### Technical Constraints
- Must integrate with existing Django backend and React frontend
- Must use existing authentication system (JWT)
- Must follow existing email notification patterns
- Must use Material-UI for consistency

### Business Constraints
- Support team of 2-3 people to handle tickets
- Expected ticket volume: 20-50 per day
- Business hours: 8 AM - 6 PM CST, Monday-Friday
- Response time goal: 2 hours for high priority, 24 hours for others

### Assumptions
- Customers have internet access to view tickets
- Email notifications will be received (not spam filtered)
- Most tickets will be order-related
- Staff will check tickets multiple times per day
- Closed tickets will not be reopened (new ticket required)

## Dependencies

### External Services
- SendGrid API for email notifications
- Existing EmailService implementation

### Existing Features
- CustomUser model (for customer and staff)
- Order model (for linking tickets to orders)
- JWT authentication system
- Django REST Framework
- React frontend with Material-UI

### Third-Party Libraries
- No new libraries required
- Uses existing Django, DRF, React, Material-UI stack

## Testing Requirements

### Backend Unit Tests
- Test ticket creation with valid data
- Test ticket number generation uniqueness
- Test customer can only view own tickets
- Test staff can view all tickets
- Test comment creation
- Test status update (staff only)
- Test priority update (staff only)
- Test ticket filtering and pagination
- Test order linking validation
- Test email notification triggering

### Frontend Component Tests
- Test TicketList renders correctly
- Test CreateTicketForm validation
- Test TicketDetail displays all information
- Test AddCommentForm submission
- Test status badge displays correct color
- Test filtering controls work
- Test pagination navigation
- Test error handling displays correctly

### Integration Tests
- Test complete ticket creation flow (backend + email)
- Test comment addition with email notification
- Test status change with history logging
- Test customer-staff interaction flow
- Test ticket search and filtering

### Manual Testing Scenarios
1. Customer creates ticket for order issue
2. Staff views ticket and adds comment
3. Customer receives email and responds
4. Staff changes status to in_progress
5. Staff resolves ticket
6. Customer views resolved ticket
7. Customer creates general inquiry ticket (no order)
8. Staff filters tickets by high priority
9. Search for ticket by number

### Performance Testing
- Load test with 100 concurrent ticket creations
- Test ticket list with 1000+ tickets
- Test pagination performance
- Test search query performance

## Future Enhancements (Not in MVP)

### Phase 2 Features
- File attachments (screenshots, documents)
- Ticket assignment to specific staff members
- Internal staff notes (not visible to customers)
- Ticket templates for common issues
- Customer satisfaction survey after resolution
- Reopen closed tickets (with approval)

### Phase 3 Features
- Live chat integration
- Ticket escalation workflow
- SLA (Service Level Agreement) tracking
- Advanced analytics dashboard
- Knowledge base integration
- Automated ticket routing based on category

## Risk Assessment

### Potential Risks
- **Email delivery issues**: Notifications may not reach customers
- **High ticket volume**: Support team overwhelmed
- **Spam/abuse**: Customers creating too many tickets
- **Performance**: Ticket list slow with large dataset
- **Status confusion**: Customers unclear about status meanings

### Mitigation Strategies
- Implement fallback SMTP if SendGrid fails
- Add rate limiting on ticket creation
- Implement pagination and search for performance
- Add clear status descriptions in UI
- Monitor ticket volume and add alerts
- Create FAQ/self-service to reduce ticket volume

## Success Metrics

### KPIs to Track
- Number of tickets created per day
- Average response time (time to first staff comment)
- Average resolution time (time from open to resolved)
- Customer satisfaction rating (post-resolution survey - future)
- Percentage of tickets resolved within SLA
- Most common ticket categories
- Peak ticket times/days

### Target Goals (After 3 Months)
- 90% of tickets receive first response within 2 hours
- 85% of tickets resolved within 24 hours
- Less than 5% of tickets require escalation
- Customer support satisfaction 4.5/5 or higher
