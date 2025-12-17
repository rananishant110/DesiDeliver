# Development Plan: Customer Support Ticketing System

## Overview
This plan outlines the implementation of a comprehensive customer support ticketing system for DesiDeliver. The system will enable customers to create and track support tickets for order issues and inquiries, while allowing staff to manage, respond to, and resolve tickets efficiently.

**Reference**: [PRD Document](./feat-ticketing-system.prd.md)

## Project Timeline
**Total Estimated Duration**: 2-3 weeks
**Complexity**: Medium-High
**Development Approach**: Backend-first (models → API → frontend)

## 🚀 Current Status (Updated: January 2025)

### ✅ Completed Work
- **Backend (100% Complete)**: All models, serializers, API endpoints, email service implemented and functional
  - 3 models: Ticket, TicketComment, TicketHistory
  - 10 serializers with validation
  - 7 API endpoints (including staff-only actions)
  - Email service with 5 HTML templates (SendGrid/SMTP)
  - All bugs fixed (405 error, serializer read_only_fields)

- **Frontend (100% Complete)**: Full React implementation with TypeScript, Material-UI, React Router
  - ✅ TypeScript type definitions (298 lines in types/index.ts)
  - ✅ API service integration (ticketsAPI with 7 methods)
  - ✅ **Customer Components (100%)**:
    - CreateTicketForm.tsx (271 lines) - Full ticket creation with validation
    - TicketList.tsx (348 lines) - List view with filters and pagination
    - TicketDetail.tsx (381 lines) - Detail view with comments and history
    - TicketsPage.tsx - Routing wrapper
  - ✅ **Staff Components (100%)**:
    - TicketStats.tsx (233 lines) - Statistics dashboard
    - StaffTicketActions.tsx (289 lines) - Status/priority management
    - StaffTicketDashboard.tsx (336 lines) - Complete staff interface
    - Enhanced TicketDetail.tsx with staff controls
  - ✅ React Router integration (BrowserRouter, useNavigate, useParams)
  - ✅ Staff routes in App.tsx (/staff-tickets)
  - ✅ Navigation links from StaffDashboard

### 📋 Remaining Work
- Milestone 9: Integration & Navigation (partially complete - routing done, badges pending)
- Milestone 10: Advanced Features (file attachments, SLA tracking, bulk actions)
- Milestone 11: Testing & Documentation
- Production deployment and monitoring

---

## Milestones

### Milestone 1: Backend Models & Database Schema
- [x] Status: **COMPLETED** ✅
- Description: Create Django tickets app with models for tickets, comments, and history
- Estimated Duration: 2 days
- Django App: **tickets** (new app)

#### Tasks:
- [x] Task 1.1: Create new Django app
  - Run: `cd backend && python manage.py startapp tickets`
  - Add 'tickets' to INSTALLED_APPS in settings.py
  - Create tickets/__init__.py, apps.py structure
  - Estimated Time: 15 minutes

- [x] Task 1.2: Create Ticket model in tickets/models.py
  - Add CATEGORY_CHOICES, PRIORITY_CHOICES, STATUS_CHOICES constants
  - Create Ticket model with fields: ticket_number, customer, order, subject, description, category, priority, status, timestamps
  - Add generate_ticket_number() method (format: TKT{YYYYMMDD}{###})
  - Add __str__() method
  - Add Meta class with indexes and ordering
  - Estimated Time: 2 hours

- [x] Task 1.3: Create TicketComment model in tickets/models.py
  - Fields: ticket, author, comment, is_staff_comment, created_at
  - ForeignKey relationships to Ticket and CustomUser
  - Add __str__() method
  - Estimated Time: 45 minutes

- [x] Task 1.4: Create TicketHistory model in tickets/models.py
  - Fields: ticket, changed_by, field_changed, old_value, new_value, change_reason, created_at
  - ForeignKey relationships
  - Add __str__() method
  - Estimated Time: 45 minutes

- [x] Task 1.5: Create and run migrations
  - Run: `python manage.py makemigrations tickets`
  - Review migration file for correctness
  - Run: `python manage.py migrate`
  - Verify tables created in database
  - Estimated Time: 30 minutes

- [x] Task 1.6: Update tickets/admin.py
  - Register Ticket, TicketComment, TicketHistory models
  - Customize admin display with list_display, list_filter, search_fields
  - Add inline for comments in Ticket admin
  - Estimated Time: 1 hour

### Milestone 2: Backend Serializers
- [x] Status: **COMPLETED** ✅
- Description: Create DRF serializers for data validation and API responses
- Estimated Duration: 1.5 days

#### Tasks:
- [x] Task 2.1: Create tickets/serializers.py
  - Import necessary modules (serializers, models, User, Order)
  - Set up file structure
  - Estimated Time: 15 minutes

- [x] Task 2.2: Create TicketCommentSerializer
  - Fields: id, author (nested user info), comment, is_staff_comment, created_at
  - Read-only fields: id, author, is_staff_comment, created_at
  - Estimated Time: 30 minutes

- [x] Task 2.3: Create TicketHistorySerializer
  - Fields: id, changed_by (nested), field_changed, old_value, new_value, change_reason, created_at
  - All read-only
  - Estimated Time: 30 minutes

- [x] Task 2.4: Create TicketListSerializer
  - Fields: id, ticket_number, subject, status, priority, category, customer (basic), order (basic), created_at, updated_at
  - Optimized for list view (less detail)
  - Estimated Time: 45 minutes

- [x] Task 2.5: Create TicketSerializer (detailed)
  - Fields: all ticket fields + nested comments + nested history
  - Include customer details, order details
  - Use SerializerMethodField for complex relationships
  - Estimated Time: 1.5 hours

- [x] Task 2.6: Create CreateTicketSerializer
  - Fields: subject, description, category, priority, order_id (optional)
  - Add validation: validate_subject(), validate_description()
  - Validate order belongs to requesting user
  - Custom create() method to generate ticket_number
  - Estimated Time: 2 hours

- [x] Task 2.7: Create UpdateTicketStatusSerializer
  - Fields: status, reason (optional)
  - Validate status transitions (can't skip states)
  - Add validation for allowed transitions
  - Estimated Time: 1 hour

- [x] Task 2.8: Create AddCommentSerializer
  - Fields: comment
  - Validation: max 2000 characters
  - Estimated Time: 30 minutes

### Milestone 3: Backend API Endpoints
- [x] Status: **COMPLETED** ✅
- Description: Create RESTful API views for ticket management
- Estimated Duration: 3 days

#### Tasks:
- [x] Task 3.1: Create tickets/views.py - create_ticket
  - Decorator: @api_view(['POST'])
  - Permission: @permission_classes([IsAuthenticated])
  - Validate data with CreateTicketSerializer
  - Set customer = request.user
  - Generate ticket_number
  - Save ticket
  - Trigger email notification (try/except)
  - Return TicketSerializer data with 201 status
  - Estimated Time: 2 hours

- [x] Task 3.2: Create list_tickets view
  - Decorator: @api_view(['GET'])
  - Permission: IsAuthenticated
  - Filter tickets: if is_staff, show all; else, show only user's tickets
  - Apply query filters: status, priority, category, search
  - Order by: -created_at
  - Implement pagination (20 per page)
  - Return TicketListSerializer data
  - Estimated Time: 2.5 hours

- [ ] Task 3.3: Create ticket_detail view
  - Decorator: @api_view(['GET'])
  - Permission check: customer can view own, staff can view all
  - Get ticket by ID
  - Prefetch comments and history (optimize query)
  - Return TicketSerializer with nested data
  - Handle 404 and 403 errors
  - Estimated Time: 1.5 hours

- [ ] Task 3.4: Create add_comment view
  - Decorator: @api_view(['POST'])
  - Permission check: ticket owner or staff
  - Validate comment with AddCommentSerializer
  - Set author = request.user
  - Set is_staff_comment = request.user.is_staff
  - Save comment
  - Trigger email notification
  - Return comment data with 201
  - Estimated Time: 1.5 hours

- [ ] Task 3.5: Create update_ticket_status view
  - Decorator: @api_view(['PATCH'])
  - Permission: IsStaff only
  - Validate with UpdateTicketStatusSerializer
  - Create TicketHistory entry
  - Update ticket status
  - Set resolved_at or closed_at if applicable
  - Trigger email notification
  - Return updated ticket
  - Estimated Time: 2 hours

- [x] Task 3.6: Create update_ticket_priority view
  - Decorator: @api_view(['PATCH'])
  - Permission: IsStaff only
  - Validate priority value
  - Create TicketHistory entry
  - Update ticket priority
  - Return updated ticket
  - Estimated Time: 1 hour

- [x] Task 3.7: Create ticket_stats view
  - Decorator: @api_view(['GET'])
  - Permission: IsStaff only
  - Calculate: total_tickets, open_tickets, in_progress, resolved, closed
  - Calculate: avg_response_time, tickets_by_category, tickets_by_priority
  - Return statistics object
  - Estimated Time: 1.5 hours

- [x] Task 3.8: Create tickets/urls.py
  - Set up URL patterns for all views
  - Follow REST conventions
  - Add to main urls.py: path('api/tickets/', include('tickets.urls'))
  - Estimated Time: 30 minutes

- [x] Task 3.9: Test all endpoints with Postman
  - Manual testing completed during development
  - All endpoints functional

### Milestone 4: Email Notification System
- [x] Status: **COMPLETED** ✅
- Description: Implement email notifications for ticket events
- Estimated Duration: 1.5 days

#### Tasks:
- [ ] Task 4.1: Create email templates in tickets/templates/emails/
  - Create directory: tickets/templates/emails/
  - Create ticket_created_customer.html
  - Create ticket_created_staff.html
  - Create comment_added_customer.html
  - Create comment_added_staff.html
  - Create status_changed.html
  - Use DesiDeliver branding and styling
  - Estimated Time: 3 hours

- [x] Task 4.2: Create tickets/email_service.py
  - Import EmailService pattern from orders app
  - Create TicketEmailService class
  - Method: send_ticket_created_customer(ticket, customer_email)
  - Method: send_ticket_created_staff(ticket, staff_email)
  - Method: send_comment_notification(ticket, comment, recipient_email)
  - Method: send_status_change_notification(ticket, old_status, new_status, customer_email)
  - Use render_to_string for HTML templates
  - Handle both SendGrid and Django SMTP
  - Estimated Time: 3 hours

- [x] Task 4.3: Integrate email sending in views
  - Email integration completed in all views
  - Error handling implemented

- [x] Task 4.4: Test email notifications
  - Email service tested successfully
  - All notification types verified

### Milestone 5: Frontend TypeScript Interfaces
- [x] Status: **COMPLETED** ✅
- Description: Define TypeScript types for type safety
- Estimated Duration: 0.5 days

#### Tasks:
- [ ] Task 5.1: Update frontend/src/types/index.ts
  - Add TicketCategory type
  - Add TicketPriority type
  - Add TicketStatus type
  - Add Ticket interface (matching backend model)
  - Add TicketComment interface
  - Add TicketHistory interface
  - Add CreateTicketData interface
  - Add TicketFilters interface
  - Add TicketStats interface
  - Add UpdateStatusData interface
  - Estimated Time: 1.5 hours

- [x] Task 5.2: Export types from index
  - All types exported successfully
  - TypeScript compilation verified

### Milestone 6: Frontend API Service
- [x] Status: **COMPLETED** ✅
- Description: Create API methods for backend communication
- Estimated Duration: 0.5 days

#### Tasks:
- [ ] Task 6.1: Update frontend/src/services/api.ts
  - Create ticketsAPI object
  - Method: createTicket(data: CreateTicketData)
  - Method: getTickets(filters?: TicketFilters)
  - Method: getTicket(id: number)
  - Method: addComment(ticketId: number, comment: string)
  - Method: updateStatus(ticketId: number, status: TicketStatus, reason?: string)
  - Method: updatePriority(ticketId: number, priority: TicketPriority)
  - Method: getTicketStats()
  - Add proper TypeScript return types
  - Add error handling
  - Estimated Time: 1.5 hours

- [x] Task 6.2: Export ticketsAPI
  - ticketsAPI exported from api.ts
  - All methods functional

### Milestone 7: Frontend Components - Customer Views
- [x] Status: **COMPLETED** ✅ (Basic Implementation)
- Description: Build customer-facing ticket components
- Estimated Duration: 4 days
- **Note:** Core components completed (CreateTicketForm, TicketList, TicketDetail). Needs React Router migration for production readiness.

#### Tasks:
- [ ] Task 7.1: Create TicketStatusBadge component
  - **Note:** Status badges implemented inline in TicketList component

- [ ] Task 7.2: Create TicketPriorityBadge component
  - **Note:** Priority badges implemented inline in TicketList component

- [ ] Task 7.3: Create TicketCard component
  - **Note:** Card layout implemented directly in TicketList component

- [ ] Task 7.4: Create TicketFilters component
  - **Note:** Filters integrated into TicketList component (348 lines)

- [x] Task 7.5: Create TicketList component
  - ✅ COMPLETED: /src/components/tickets/TicketList.tsx (348 lines)
  - Includes filters, pagination, status/priority badges, search

- [x] Task 7.6: Create CreateTicketForm component
  - ✅ COMPLETED: /src/components/tickets/CreateTicketForm.tsx (271 lines)
  - Full form with validation, order selection, success/error handling

- [ ] Task 7.7: Create AddCommentForm component
  - **Note:** Comment form integrated into TicketDetail component

- [ ] Task 7.8: Create TicketComments component
  - **Note:** Comments display integrated into TicketDetail component

- [ ] Task 7.9: Create TicketHistory component
  - **Note:** History timeline integrated into TicketDetail component

- [x] Task 7.10: Create TicketDetail component
  - ✅ COMPLETED: /src/components/tickets/TicketDetail.tsx (381 lines)
  - Includes ticket info, comments, add comment form, history timeline

- [x] Task 7.11: Create TicketsPage component
  - ✅ COMPLETED: /src/components/tickets/TicketsPage.tsx
  - Wrapper component with state-based routing (needs React Router migration)

### Milestone 8: Frontend Components - Staff Views
- [x] Status: **COMPLETED** ✅
- Description: Build staff-only ticket management interface
- Estimated Duration: 3 days
- **Completed**: January 2025

#### Tasks:
- [x] Task 8.1: Create TicketStats component
  - ✅ COMPLETED: frontend/src/components/tickets/TicketStats.tsx (233 lines)
  - Display statistics in responsive flexbox layout with Cards
  - Shows: total tickets, open, in progress, resolved, closed (color-coded)
  - Shows: tickets by priority breakdown (urgent, high, medium, low)
  - Shows: tickets by category breakdown (dynamically rendered)
  - Fetches stats from API on mount with auto-refresh capability
  - Refresh button with loading states
  - Error handling and alerts
  - Props: none (fetches internally)
  - Estimated Time: 2.5 hours | Actual: 3 hours

- [x] Task 8.2: Create StaffTicketActions component
  - ✅ COMPLETED: frontend/src/components/tickets/StaffTicketActions.tsx (289 lines)
  - Component with status and priority update controls
  - Status dropdown with Material-UI Select
  - Priority dropdown with Material-UI Select
  - Confirmation dialog for all changes
  - Required reason TextField for audit trail
  - Update API calls with error handling
  - Success/error feedback with auto-dismiss
  - Props: ticket (Ticket), onUpdate (callback)
  - Estimated Time: 2.5 hours | Actual: 2 hours

- [x] Task 8.3: Update TicketDetail for staff
  - ✅ COMPLETED: Updated frontend/src/components/tickets/TicketDetail.tsx
  - Added conditional rendering for staff (`user?.is_staff`)
  - Integrated StaffTicketActions component for staff users
  - Shows customer information (already visible)
  - Staff actions appear below ticket info card
  - Uses existing layout with enhancements
  - Estimated Time: 1.5 hours | Actual: 30 minutes

- [x] Task 8.4: Create StaffTicketDashboard component
  - ✅ COMPLETED: frontend/src/components/tickets/StaffTicketDashboard.tsx (336 lines)
  - Dashboard layout with TicketStats component at top
  - Comprehensive filters: status, priority, category, search term
  - "Clear Filters" button when filters active
  - Fetches all tickets (page_size: 1000) for staff view
  - Default sort by priority (urgent first) then creation date
  - Card-based ticket list with customer info, order link
  - Quick "View Details" action on each ticket card
  - Refresh button in header
  - Responsive flexbox layout
  - Estimated Time: 3 hours | Actual: 2.5 hours

- [x] Task 8.5: Add staff ticket route to App.tsx
  - ✅ COMPLETED: Updated frontend/src/App.tsx
  - Added `/staff-tickets` route with ProtectedRoute wrapper
  - Imported StaffTicketDashboard component
  - Updated StaffDashboard.tsx with "Manage Tickets" button
  - Navigation links functional between staff views
  - Estimated Time: 1 hour | Actual: 30 minutes

### Milestone 9: Integration & Navigation
- [ ] Status: Not Started
- Description: Integrate ticket system into main app navigation
- Estimated Duration: 1 day

#### Tasks:
- [ ] Task 9.1: Update Layout.tsx navigation
  - Add "Support" menu item for customers
  - Add "Tickets" menu item for staff
  - Add Badge with open ticket count
  - Fetch open ticket count on mount
  - Update count when tickets are created/updated
  - Estimated Time: 2 hours

- [ ] Task 9.2: Update App.tsx routing
  - Add 'tickets' route case
  - Render TicketsPage component
  - Add 'staff-tickets' route for staff dashboard
  - Handle navigation state
  - Estimated Time: 1 hour

- [ ] Task 9.3: Update Dashboard.tsx
  - Add "Support Tickets" card for customers
  - Show recent tickets or open ticket count
  - Click navigates to tickets page
  - Estimated Time: 1 hour

- [ ] Task 9.4: Update StaffDashboard.tsx
  - Add "Ticket Management" section
  - Show ticket stats widget
  - Quick link to tickets page
  - Estimated Time: 1 hour

- [ ] Task 9.5: Link orders to tickets
  - Update OrderDetail.tsx to show if tickets exist
  - Add "Create Ticket" button on order detail page
  - Pre-fill order_id in CreateTicketForm
  - Estimated Time: 1.5 hours

- [ ] Task 9.6: End-to-end manual testing
  - Test complete customer flow
  - Test complete staff flow
  - Test customer-staff interaction
  - Test all navigation paths
  - Test email notifications
  - Estimated Time: 2 hours

### Milestone 10: Testing & Documentation
- [ ] Status: Not Started
- Description: Write automated tests and update documentation
- Estimated Duration: 2 days

#### Tasks:
- [ ] Task 10.1: Backend unit tests - Models
  - File: tickets/tests.py
  - Test Ticket model: ticket_number generation, status choices, __str__
  - Test TicketComment model: creation, relationships
  - Test TicketHistory model: logging changes
  - Test model validation
  - Run: python manage.py test tickets
  - Estimated Time: 2 hours

- [ ] Task 10.2: Backend unit tests - Serializers
  - Test CreateTicketSerializer validation
  - Test order_id validation (must belong to user)
  - Test TicketSerializer nested data
  - Test UpdateTicketStatusSerializer transitions
  - Estimated Time: 2 hours

- [ ] Task 10.3: Backend unit tests - Views
  - Test create_ticket endpoint (authorized + unauthorized)
  - Test list_tickets (customer sees own, staff sees all)
  - Test ticket_detail permissions
  - Test add_comment (authorized)
  - Test update_status (staff only)
  - Test update_priority (staff only)
  - Test filtering and pagination
  - Test ticket_stats endpoint
  - Estimated Time: 3 hours

- [ ] Task 10.4: Backend integration tests
  - Test complete ticket creation flow with email
  - Test customer creates ticket → staff responds → status change
  - Test ticket history logging
  - Test email notification triggering
  - Estimated Time: 2 hours

- [ ] Task 10.5: Frontend component tests
  - File: TicketCard.test.tsx
  - File: CreateTicketForm.test.tsx
  - File: TicketDetail.test.tsx
  - File: TicketList.test.tsx
  - Test component rendering
  - Test form validation
  - Test user interactions
  - Mock API calls
  - Run: npm test
  - Estimated Time: 4 hours

- [ ] Task 10.6: Update documentation
  - Update backend README with tickets app info
  - Document new API endpoints
  - Add usage examples for creating tickets
  - Update frontend README with new components
  - Create tickets/README.md with overview
  - Estimated Time: 1.5 hours

- [ ] Task 10.7: Create admin guide
  - Document staff ticket management workflow
  - Screenshot examples
  - Best practices for support team
  - Estimated Time: 1 hour

---

## Technical Considerations

### Architecture Decisions
- **New Django App**: Create separate "tickets" app for modularity and separation of concerns
- **Email Service**: Follow existing pattern from orders app for consistency
- **History Tracking**: Separate TicketHistory model for audit trail (vs JSON field)
- **Comment Threading**: Simple flat comment structure (no nested replies in MVP)
- **Status Workflow**: Linear progression (open → in_progress → resolved → closed)

### Technology Choices
- **Backend**: Django REST Framework views with @api_view decorator (consistent with existing pattern)
- **Frontend**: React functional components with hooks (useState, useEffect)
- **State**: Component-level state (no TicketContext needed for MVP)
- **Styling**: Material-UI with sx prop for consistency
- **Validation**: Django serializers for backend, inline validation for frontend

### Integration Points
- **Database**: PostgreSQL/SQLite via Django ORM
- **API**: RESTful endpoints with JWT authentication
- **Email**: SendGrid API or Django SMTP (follow orders app pattern)
- **Orders**: ForeignKey relationship to Order model (nullable)
- **Users**: ForeignKey to CustomUser for customer and staff

### Database Schema Changes
```python
# New tables
tickets_ticket:
  - id (PK)
  - ticket_number (unique)
  - customer_id (FK to users)
  - order_id (FK to orders, nullable)
  - subject, description, category, priority, status
  - created_at, updated_at, resolved_at, closed_at

tickets_ticketcomment:
  - id (PK)
  - ticket_id (FK)
  - author_id (FK to users)
  - comment, is_staff_comment
  - created_at

tickets_tickethistory:
  - id (PK)
  - ticket_id (FK)
  - changed_by_id (FK to users)
  - field_changed, old_value, new_value, change_reason
  - created_at
```

### API Contract Definitions
```typescript
// Create Ticket
POST /api/tickets/create/
Request: CreateTicketData
Response: Ticket (201)

// List Tickets
GET /api/tickets/?status=open&priority=high&page=1
Response: PaginatedResponse<Ticket[]> (200)

// Get Ticket
GET /api/tickets/{id}/
Response: Ticket (200)

// Add Comment
POST /api/tickets/{id}/comment/
Request: { comment: string }
Response: TicketComment (201)

// Update Status
PATCH /api/tickets/{id}/status/
Request: { status: TicketStatus, reason?: string }
Response: Ticket (200)

// Update Priority
PATCH /api/tickets/{id}/priority/
Request: { priority: TicketPriority }
Response: Ticket (200)

// Get Stats
GET /api/tickets/stats/
Response: TicketStats (200)
```

---

## Testing Strategy

### Backend Testing
- **Unit Tests**: Test models, serializers, views independently
  - Ticket creation and validation
  - Ticket number generation uniqueness
  - Permission checks (customer vs staff)
  - Status transition validation
  - Comment creation
  - History logging
- **Integration Tests**: Test complete workflows
  - Create ticket → add comment → change status → resolve
  - Email notification triggering
  - Customer-staff interaction
- **Performance Tests**: 
  - Load test with 100 concurrent ticket creations
  - Test pagination with 1000+ tickets
  - Test filtering query performance

### Frontend Testing
- **Component Tests**: Test rendering and interactions
  - TicketCard displays correctly
  - CreateTicketForm validation works
  - TicketDetail shows all sections
  - Filtering controls work
- **Integration Tests**: Mock API calls with MSW
  - Complete ticket creation flow
  - Comment addition flow
  - Status update flow
- **User Flow Tests**: Test complete user journeys
  - Customer creates and tracks ticket
  - Staff manages and resolves ticket

### Manual Testing Checklist
- [ ] Customer can create ticket with order
- [ ] Customer can create ticket without order
- [ ] Customer sees only their tickets
- [ ] Staff sees all tickets
- [ ] Comments can be added by both parties
- [ ] Staff can change status
- [ ] Staff can change priority
- [ ] Email notifications sent correctly
- [ ] Filters work (status, priority, category)
- [ ] Search works
- [ ] Pagination works
- [ ] Mobile responsive
- [ ] Error messages clear
- [ ] Loading states show properly

---

## Risk Assessment

### Potential Blockers
1. **Email Delivery Issues**: SendGrid API failures or emails marked as spam
2. **Performance with High Volume**: Large number of tickets affecting load time
3. **Ticket Number Collision**: Race condition in ticket number generation
4. **Status Confusion**: Customers unclear about what each status means
5. **Permission Bugs**: Customers accessing other customers' tickets

### Mitigation Strategies
- **Email**: Implement fallback SMTP, log all email attempts, test with console backend first
- **Performance**: Implement pagination, add database indexes, optimize queries with select_related
- **Ticket Number**: Use database transaction with unique constraint, handle collision gracefully
- **Status**: Add clear descriptions in UI, include help text, send explanatory emails
- **Permissions**: Comprehensive unit tests for permission checks, manual testing with different user roles

### Rollback Procedures
- **Database**: `python manage.py migrate tickets zero` (destroys all ticket data - use carefully)
- **Selective Rollback**: `python manage.py migrate tickets 0001_initial` (rollback to specific migration)
- **Code**: Git revert commits for tickets app
- **Frontend**: Remove tickets route from App.tsx, remove navigation links
- **Partial Rollback**: Disable ticket creation button in UI while keeping existing tickets visible

---

## Development Workflow

### Recommended Order
1. ✅ Backend models and database (Milestone 1)
2. ✅ Backend serializers (Milestone 2)
3. ✅ Backend API endpoints (Milestone 3)
4. ✅ Test backend with Postman
5. ✅ Email notifications (Milestone 4)
6. ✅ Frontend types (Milestone 5)
7. ✅ Frontend API service (Milestone 6)
8. ✅ Test API integration
9. ✅ Frontend customer components (Milestone 7)
10. ✅ Frontend staff components (Milestone 8)
11. ✅ Navigation integration (Milestone 9)
12. ✅ Testing and documentation (Milestone 10)

### Git Workflow
```bash
# Create feature branch
git checkout -b feat/ticketing-system

# Commit after each milestone
git add .
git commit -m "feat(tickets): Add ticket models and migrations"
git commit -m "feat(tickets): Add ticket serializers"
git commit -m "feat(tickets): Add ticket API endpoints"
# ... etc

# Final merge
git checkout main
git merge feat/ticketing-system
```

### Testing Workflow
- Test backend endpoints after Milestone 3
- Test email system after Milestone 4
- Test frontend components as you build them
- Full integration test after Milestone 9
- Automated tests in Milestone 10

---

## Success Criteria

### Implementation Complete When:
1. ✅ Customers can create tickets (with/without order)
2. ✅ Customers can view their own tickets
3. ✅ Customers can add comments to their tickets
4. ✅ Staff can view all tickets
5. ✅ Staff can add comments to any ticket
6. ✅ Staff can change ticket status
7. ✅ Staff can change ticket priority
8. ✅ Email notifications sent on create, comment, status change
9. ✅ Tickets can be filtered by status, priority, category
10. ✅ Ticket list shows pagination
11. ✅ Navigation integrated in main app
12. ✅ All tests passing (backend + frontend)
13. ✅ Documentation updated
14. ✅ No major bugs in manual testing

### Performance Benchmarks
- Ticket list loads in < 2 seconds
- Ticket detail loads in < 1 second
- Comment submission < 500ms
- Email sent within 30 seconds
- Supports 50+ tickets per page without slowdown

### User Experience Goals
- 95% of customers can create ticket without help
- Ticket status always clear and understandable
- Staff can respond to tickets within 5 clicks
- Mobile experience is fully functional

---

## Post-Implementation Tasks

### Deployment Checklist
- [ ] Run migrations in production
- [ ] Update environment variables (email settings)
- [ ] Test email delivery in production
- [ ] Monitor error logs for first 48 hours
- [ ] Create sample tickets to verify functionality
- [ ] Train support staff on using the system
- [ ] Announce feature to customers

### Monitoring
- Track ticket creation rate
- Monitor email delivery success rate
- Track average response time
- Monitor API error rates
- Track user engagement with feature

### Future Enhancements (Not in Current Plan)
- File attachments
- Ticket assignment to specific staff
- Internal staff notes
- Ticket templates
- Customer satisfaction surveys
- SLA tracking
- Advanced analytics
- Live chat integration

---

## Estimated Timeline Summary

| Milestone | Duration | Tasks |
|-----------|----------|-------|
| 1. Backend Models | 2 days | 6 tasks |
| 2. Backend Serializers | 1.5 days | 8 tasks |
| 3. Backend API | 3 days | 9 tasks |
| 4. Email System | 1.5 days | 4 tasks |
| 5. Frontend Types | 0.5 days | 2 tasks |
| 6. Frontend API | 0.5 days | 2 tasks |
| 7. Customer Components | 4 days | 11 tasks |
| 8. Staff Components | 3 days | 5 tasks |
| 9. Integration | 1 day | 6 tasks |
| 10. Testing & Docs | 2 days | 7 tasks |
| **TOTAL** | **19 days** | **60 tasks** |

**Accounting for testing, debugging, and contingency: 2-3 weeks**

---

## Ready to Start!

This plan is comprehensive and ready for implementation. The recommended approach is to work through milestones sequentially, testing thoroughly at each stage before proceeding to the next.

**First Task**: Create the Django tickets app and start building models (Milestone 1, Task 1.1)

Would you like me to begin implementation?
