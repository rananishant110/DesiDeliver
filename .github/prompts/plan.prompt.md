---
mode: agent
---

# DesiDeliver Feature Planning & Development Guide

## Mission
This prompt assists with planning, documenting, and organizing feature development for DesiDeliver - an Indian grocery supply management system. It ensures structured documentation before development, maintains consistency across planning documents, and aligns with established architecture patterns.

---

## Project Context

**CRITICAL**: Before starting any planning, invoke the `learn.prompt.md` if you haven't already to understand the complete application architecture.

### Technology Stack
- **Frontend**: React 19.1.1 + TypeScript 4.9.5 + Material-UI 7.3.1
- **Backend**: Django 5.2.5 + Django REST Framework 3.16.1 + PostgreSQL/SQLite
- **Authentication**: JWT (djangorestframework-simplejwt) with access/refresh tokens
- **Email**: SendGrid API / Django SMTP backend
- **State Management**: React Context API (AuthContext, CartContext)
- **HTTP Client**: Axios 1.11.0 with interceptors

### Application Architecture
- **Backend**: Django apps (users, products, cart, orders) with Models → Serializers → Views → URLs pattern
- **Frontend**: Component-based architecture with /auth, /catalog, /cart, /orders, /staff, /common modules
- **API Structure**: RESTful endpoints at /api/{module}/ with JWT authentication
- **Database**: Relational model with ForeignKey relationships (User → Cart → CartItem → Product, User → Order → OrderItem → Product)
- **Business Domain**: B2B grocery ordering for DFW area restaurants/stores with automated CSV generation and email notifications 

## Documentation Structure

### Directory Organization
All documentation must be stored in the `docs` directory. The structure is maintained in `docs/tree.md`.

#### Directory Naming Convention
- **Features**: `feat-<feature-name>` (e.g., `feat-user-authentication`, `feat-goal-setting-api`)
- **Fixes**: `fix-<issue-name>` (e.g., `fix-login-error`, `fix-auth-password`)

#### File Naming Convention
Within each feature/fix directory:
- PRD Document: `<directory-name>.prd.md`
- Plan Document: `<directory-name>.plan.md`

Example structure:
```
docs/
├── tree.md
├── feat-goal-setting-api/
│   ├── feat-goal-setting-api.prd.md
│   └── feat-goal-setting-api.plan.md
├── feat-debt-api/
│   ├── feat-debt-api.prd.md
│   └── feat-debt-api.plan.md
└── fix-auth-password/
   ├── fix-auth-password.prd.md
   └── fix-auth-password.plan.md
```

### Initial Setup
1. If `docs` directory doesn't exist, create it at `/Users/neelam/Desktop/apps/DesiDeliver/docs/`
2. If `docs/tree.md` doesn't exist, create it with initial structure
3. Always read `docs/tree.md` first to understand existing documentation
4. Review existing features: `feat-desi-deliver-app` (main application PRD and plan)

---

## Workflow Phases

### Phase 0: Context Loading (MANDATORY)
**Before any planning work:**

1. **Load Application Knowledge (First time only)**
   - If not already familiar with DesiDeliver architecture, invoke `learn.prompt.md`
   - Understand the overall tech stack and patterns (this is for YOUR understanding, not copied to the plan)

2. **Check Current Implementation Status (Only if modifying existing features)**
   - Review `/docs/feat-desi-deliver-app/feat-desi-deliver-app.plan.md` to see what's already implemented
   - **Purpose**: Avoid planning features that already exist, or build on top of completed work
   - **Example**: If planning "Advanced Search", check if basic search milestone is completed

3. **Understand Existing Codebase (Quick check)**
   - Identify which Django app(s) the NEW feature affects: users, products, cart, orders
   - Determine which frontend modules will be impacted
   - Check for existing similar features to follow patterns (not copy milestones)
   - **Purpose**: Ensure new feature follows existing code patterns

4. **Clarify New Feature Scope**
   - Ask targeted questions about the NEW feature:
     - User role (customer vs staff)
     - Frontend UI requirements
     - Backend API requirements
     - Database schema changes
     - Email notifications needed
     - CSV export requirements
     - Integration with existing features (cart, orders, products)

**IMPORTANT**: Old milestones are NOT copied to new plans. Phase 0 is about understanding context, not copying structure.

### When to Reference Old Plans vs Create Fresh Plans

**Reference Old Plans When:**
- ✅ **Modifying existing feature**: Check which milestones are complete
  - Example: "Add email notification to orders" → Check orders plan to see what's already built
- ✅ **Building dependent feature**: Verify prerequisite features are complete
  - Example: "Order tracking" requires Order creation milestone to be complete
- ✅ **Fixing bugs**: Reference the original implementation plan to understand what was built
  - Example: "Fix cart validation" → Check cart plan to understand original design

**Create Fresh Plans When:**
- ✅ **New feature**: Brand new functionality (like "Order cancellation", "Wishlist", "Product reviews")
- ✅ **Independent feature**: Doesn't build on incomplete work
- ✅ **Separate module**: New Django app or frontend module

**The Plan Template (Milestones 1-10) Below:**
- These are **STRUCTURE TEMPLATES** for creating NEW feature plans
- They show **what sections to include** and **what order to follow**
- They are NOT copied from old features
- Customize them for each new feature

---

## Workflow Phases

### Phase 1: PRD Document Creation
When asked to create a new feature or fix:

1. **Understand Requirements**
   - Gather all user requirements through clarifying questions
   - Identify the problem being solved
   - Define success criteria
   - **Consider existing DesiDeliver patterns:**
     - Does it need authentication? (JWT token required)
     - Does it involve products? (Reference Product model)
     - Does it need staff permissions? (Check is_staff flag)
     - Does it send emails? (Use EmailService class)
     - Does it generate files? (Follow CSVGenerator pattern)

2. **Create PRD Document**
   - Create appropriate directory: `docs/feat-<name>` or `docs/fix-<name>`
   - Create PRD file: `<directory-name>.prd.md`
   - **DesiDeliver-Specific PRD Sections:**
      - **Title**: Feature/Fix name with clear action verb
      - **Overview**: Brief description (2-3 sentences)
      - **Problem Statement**: What problem this solves for restaurant owners or delivery coordinators
      - **User Stories**: 
        - As a restaurant owner/store owner...
        - As a delivery coordinator...
        - As a system administrator...
      - **Functional Requirements**: 
        - Detailed feature specifications
        - User interactions and workflows
        - Business logic and rules
      - **Technical Requirements**:
        - **Backend Changes**:
          - Django app affected (users/products/cart/orders)
          - New models or model changes (with field specifications)
          - New serializers or updates
          - New views/endpoints or updates
          - URL routing changes
        - **Frontend Changes**:
          - New components or component updates
          - Context updates (AuthContext, CartContext)
          - New API service methods
          - TypeScript interface updates
          - Routing/navigation changes
        - **Database Changes**:
          - New tables or columns
          - Migrations required
          - Indexes needed
          - Relationships (ForeignKey, ManyToMany)
      - **API Specifications**: 
        ```
        Endpoint: POST /api/{module}/{action}/
        Authentication: Required (JWT)
        Permissions: IsAuthenticated / IsStaff
        Request Body: {TypeScript interface}
        Response: {TypeScript interface}
        Status Codes: 200, 201, 400, 401, 404, 500
        ```
      - **UI/UX Requirements**: 
        - Material-UI components to use
        - User flows with step-by-step interactions
        - Form validation rules
        - Error handling and messaging
        - Loading states and feedback
      - **Email Notifications** (if applicable):
        - Who receives emails?
        - Email templates needed
        - When are emails triggered?
      - **CSV/File Generation** (if applicable):
        - File format and structure
        - When generated?
        - Who can download?
      - **Success Criteria**: 
        - Functional acceptance criteria
        - Performance requirements
        - User experience goals
      - **Security Considerations**:
        - Authentication requirements
        - Authorization/permissions
        - Input validation and sanitization
        - SQL injection prevention
        - XSS prevention
      - **Constraints & Assumptions**: 
        - Technical limitations
        - Business rules
        - Dependencies on existing features
      - **Dependencies**: 
        - External services (SendGrid)
        - Existing models/APIs
        - Third-party libraries
      - **Testing Requirements**:
        - Backend unit tests (models, views, serializers)
        - Frontend component tests
        - Integration tests
        - Manual testing scenarios

3. **Update Tree Documentation**
   - Add new directory to `docs/tree.md`
   - Include brief description of the feature/fix
   - Maintain alphabetical ordering within categories

### Phase 2: Plan Document Creation
After PRD approval:

1. **Analyze Implementation Scope**
   - Determine which files need creation vs modification
   - Identify existing patterns to follow
   - Check for reusable components/utilities
   - Estimate complexity and duration

2. **Create Plan Document**
   - Create file: `<directory-name>.plan.md`
   - Structure with milestones and tasks
   - Follow DesiDeliver development patterns
   - Consider backend-first approach (models → serializers → views → frontend)

3. **DesiDeliver-Specific Plan Structure**
   
   **NOTE**: The structure below is a TEMPLATE for creating NEW feature plans. 
   It is NOT copied from old plans. Customize it for each new feature.
   
   ```markdown
   # Development Plan: [Feature Name]
   
   ## Overview
   Brief summary with link to PRD
   Reference: [PRD Document](./<directory-name>.prd.md)
   
   ## Project Timeline
   **Total Estimated Duration**: X weeks/days
   **Complexity**: Low/Medium/High
   **Development Approach**: Backend-first / Full-stack parallel
   
   ## Milestones
   
   ### Milestone 1: Backend Models & Database
   - [ ] Status: Not Started
   - Description: Create/modify Django models and run migrations
   - Estimated Duration: X days
   - Django App: users/products/cart/orders
   
   #### Tasks:
   - [ ] Task 1.1: Update/Create models in {app}/models.py
     - Add fields: {list fields with types}
     - Add validation methods
     - Add helper methods
     - Estimated Time: X hours
   
   - [ ] Task 1.2: Create migrations
     - Run: python manage.py makemigrations
     - Review migration file
     - Run: python manage.py migrate
     - Estimated Time: 30 mins
   
   - [ ] Task 1.3: Update admin interface in {app}/admin.py
     - Register new models
     - Customize admin display
     - Estimated Time: 1 hour
   
   ### Milestone 2: Backend Serializers & Validation
   - [ ] Status: Not Started
   - Description: Create DRF serializers for data validation
   - Estimated Duration: X days
   
   #### Tasks:
   - [ ] Task 2.1: Create/update serializers in {app}/serializers.py
     - Define serializer classes
     - Add validation methods (validate_*)
     - Handle nested serialization
     - Estimated Time: X hours
   
   - [ ] Task 2.2: Add custom validation logic
     - Business rule validation
     - Cross-field validation
     - Estimated Time: X hours
   
   ### Milestone 3: Backend API Endpoints
   - [ ] Status: Not Started
   - Description: Create RESTful API views and endpoints
   - Estimated Duration: X days
   
   #### Tasks:
   - [ ] Task 3.1: Create/update views in {app}/views.py
     - Use @api_view decorator or ViewSets
     - Add @permission_classes([IsAuthenticated])
     - Implement business logic
     - Add error handling
     - Estimated Time: X hours
   
   - [ ] Task 3.2: Update URL routing in {app}/urls.py
     - Add new routes
     - Follow REST conventions
     - Estimated Time: 30 mins
   
   - [ ] Task 3.3: Test endpoints with Postman/curl
     - Test all HTTP methods
     - Test authentication
     - Test error cases
     - Estimated Time: 1 hour
   
   ### Milestone 4: Email/File Services (if applicable)
   - [ ] Status: Not Started
   - Description: Implement email notifications or file generation
   - Estimated Duration: X days
   
   #### Tasks:
   - [ ] Task 4.1: Create email templates in orders/templates/
     - HTML email template
     - Text fallback
     - Estimated Time: 2 hours
   
   - [ ] Task 4.2: Update EmailService in orders/email_service.py
     - Add new email method
     - Test with console backend
     - Estimated Time: 2 hours
   
   - [ ] Task 4.3: Add CSV generation (if needed)
     - Follow CSVGenerator pattern
     - Add download endpoint
     - Estimated Time: 2 hours
   
   ### Milestone 5: Frontend TypeScript Interfaces
   - [ ] Status: Not Started
   - Description: Define TypeScript types for type safety
   - Estimated Duration: X hours
   
   #### Tasks:
   - [ ] Task 5.1: Update src/types/index.ts
     - Add new interfaces matching backend models
     - Update existing interfaces if needed
     - Add API response types
     - Estimated Time: 1 hour
   
   ### Milestone 6: Frontend API Service
   - [ ] Status: Not Started
   - Description: Create API methods for backend communication
   - Estimated Duration: X hours
   
   #### Tasks:
   - [ ] Task 6.1: Update src/services/api.ts
     - Add new API methods to appropriate module (authAPI, productsAPI, etc.)
     - Use axios with proper typing
     - Add error handling
     - Estimated Time: 1-2 hours
   
   ### Milestone 7: Frontend Context Updates (if needed)
   - [ ] Status: Not Started
   - Description: Update global state management
   - Estimated Duration: X hours
   
   #### Tasks:
   - [ ] Task 7.1: Update AuthContext or CartContext
     - Add new state properties
     - Add new actions
     - Update reducer
     - Estimated Time: 2 hours
   
   ### Milestone 8: Frontend Components
   - [ ] Status: Not Started
   - Description: Create/update React components
   - Estimated Duration: X days
   
   #### Tasks:
   - [ ] Task 8.1: Create component files in src/components/{module}/
     - Main container component
     - Child components
     - Use Material-UI components
     - Estimated Time: X hours
   
   - [ ] Task 8.2: Implement component logic
     - State management with useState
     - API calls with useEffect
     - Form handling
     - Error handling
     - Loading states
     - Estimated Time: X hours
   
   - [ ] Task 8.3: Add styling with Material-UI
     - Use sx prop or styled components
     - Responsive design
     - Follow existing theme
     - Estimated Time: X hours
   
   ### Milestone 9: Integration & Navigation
   - [ ] Status: Not Started
   - Description: Integrate new feature into app navigation
   - Estimated Duration: X hours
   
   #### Tasks:
   - [ ] Task 9.1: Update App.tsx or Layout.tsx
     - Add route handling
     - Update navigation menu
     - Estimated Time: 1 hour
   
   - [ ] Task 9.2: Test complete user flow
     - End-to-end manual testing
     - Test all user interactions
     - Estimated Time: 2 hours
   
   ### Milestone 10: Testing & Documentation
   - [ ] Status: Not Started
   - Description: Write tests and update documentation
   - Estimated Duration: X days
   
   #### Tasks:
   - [ ] Task 10.1: Backend unit tests
     - Create/update {app}/tests.py
     - Test models, serializers, views
     - Run: python manage.py test {app}
     - Estimated Time: 3 hours
   
   - [ ] Task 10.2: Frontend component tests
     - Create *.test.tsx files
     - Test component rendering and interactions
     - Run: npm test
     - Estimated Time: 3 hours
   
   - [ ] Task 10.3: Update documentation
     - Update README if needed
     - Document new API endpoints
     - Add usage examples
     - Estimated Time: 1 hour
   
   ## Technical Considerations
   
   ### Architecture Decisions
   - Follow existing Django app structure
   - Use DRF serializers for validation
   - Follow JWT authentication pattern
   - Use Material-UI components in frontend
   
   ### Technology Choices
   - **Backend**: Django REST Framework views
   - **Frontend**: React functional components with hooks
   - **State**: Context API (avoid prop drilling)
   - **Styling**: Material-UI with sx prop
   
   ### Integration Points
   - **Database**: PostgreSQL/SQLite via Django ORM
   - **API**: RESTful endpoints with JWT auth
   - **Email**: SendGrid API or Django SMTP
   - **State Management**: React Context API
   
   ### Database Schema Changes
   ```python
   # Example model changes
   class ModelName(models.Model):
       field_name = models.CharField(max_length=100)
       # ... migrations will be created
   ```
   
   ### API Contract Definitions
   ```typescript
   // Request
   interface CreateRequest {
     field: string;
   }
   
   // Response
   interface CreateResponse {
     id: number;
     field: string;
   }
   ```
   
   ## Testing Strategy
   
   ### Backend Testing
   - **Unit Tests**: Test models, serializers, views independently
   - **Integration Tests**: Test complete API workflows
   - **Authentication Tests**: Test JWT token handling
   - **Validation Tests**: Test all input validation
   
   ### Frontend Testing
   - **Component Tests**: Test rendering and user interactions
   - **Context Tests**: Test state management
   - **API Integration Tests**: Mock API calls with MSW
   - **User Flow Tests**: Test complete user journeys
   
   ### Manual Testing Checklist
   - [ ] Authentication flow works
   - [ ] API endpoints respond correctly
   - [ ] UI displays data properly
   - [ ] Forms validate correctly
   - [ ] Error messages are clear
   - [ ] Loading states show properly
   - [ ] Mobile responsive
   - [ ] Email notifications sent (if applicable)
   - [ ] CSV generation works (if applicable)
   
   ## Risk Assessment
   
   ### Potential Blockers
   - Database migration conflicts
   - Authentication/permission issues
   - Frontend-backend data format mismatches
   - Email delivery failures (SendGrid)
   
   ### Mitigation Strategies
   - Review existing migrations before creating new ones
   - Test API endpoints with Postman before frontend integration
   - Use TypeScript interfaces to ensure type consistency
   - Test email sending with console backend first
   - Keep backup of database before migrations
   
   ### Rollback Procedures
   - Database: `python manage.py migrate {app} {previous_migration}`
   - Code: Git revert commits
   - Frontend: Revert component changes
   ```

## Documentation Standards

### PRD Standards for DesiDeliver
- Use clear, concise language appropriate for B2B grocery domain
- Include Mermaid diagrams for complex workflows:
  ```mermaid
  sequenceDiagram
    Customer->>API: Create Order
    API->>Database: Save Order
    API->>EmailService: Send Notifications
  ```
- Reference existing DesiDeliver components:
  - Models: CustomUser, Product, Category, Cart, CartItem, Order, OrderItem
  - Serializers: Follow existing naming pattern (ModelSerializer)
  - Views: Use @api_view or ViewSets consistently
  - Components: Follow /auth, /catalog, /cart, /orders structure
- Define clear TypeScript interfaces matching Django models
- Specify Material-UI components for UI elements
- Consider both customer and staff user perspectives
- Include mobile responsiveness requirements
- Define validation rules matching Django validators

### Plan Standards for DesiDeliver
- **Backend-First Approach**: Start with models, then serializers, then views, then frontend
- **Atomic Tasks**: Each task 1-4 hours, clearly defined
- **File-Specific**: Reference exact file paths:
  - Backend: `/backend/{app}/{file}.py`
  - Frontend: `/frontend/src/{module}/{file}.tsx`
- **Migration Awareness**: Note when `makemigrations` and `migrate` needed
- **Testing Requirements**: Specify tests for each Django app
- **Dependencies**: Note task dependencies (Task 2.1 requires Task 1.1 complete)
- **Command References**: Include Django/npm commands to run

### Version Control
- Commit documentation changes with descriptive messages:
   - `docs: Add PRD for <feature-name>`
   - `docs: Add development plan for <feature-name>`
   - `docs: Update tree.md with <feature-name>`
- Create feature branch before starting implementation:
   - `git checkout -b feat/<feature-name>`
   - `git checkout -b fix/<issue-name>`
- Follow conventional commits for code changes:
   - `feat(orders): Add order cancellation endpoint`
   - `fix(cart): Fix quantity validation bug`
   - `test(products): Add product search tests`
   - `docs: Update API documentation`

---

## Quality Checks

Before completing any phase, verify:

### PRD Quality Checklist
- [ ] All required sections are present and complete
- [ ] Problem statement clearly defines the business need
- [ ] User stories cover all user types (customer, staff, admin)
- [ ] Technical requirements specify exact Django apps and files affected
- [ ] API specifications include full request/response examples
- [ ] TypeScript interfaces match Django model fields
- [ ] UI/UX requirements specify Material-UI components
- [ ] Security considerations address auth, permissions, and validation
- [ ] Success criteria are measurable and specific
- [ ] Dependencies on existing features are documented
- [ ] Testing requirements are comprehensive

### Plan Quality Checklist
- [ ] Milestones follow logical development order (backend → frontend)
- [ ] Each task has clear deliverable and time estimate
- [ ] Database migration tasks are included where needed
- [ ] API endpoint testing tasks are included
- [ ] Frontend type definitions are updated before components
- [ ] Integration points with existing code are identified
- [ ] Testing milestone includes backend and frontend tests
- [ ] Risk assessment covers common DesiDeliver issues
- [ ] Rollback procedures are documented
- [ ] Total time estimate is realistic

### DesiDeliver-Specific Checks
- [ ] JWT authentication requirements considered
- [ ] Material-UI theme consistency maintained
- [ ] Django app structure followed (models → serializers → views → urls)
- [ ] React component structure followed (containers, presentational)
- [ ] Context API usage considered for global state
- [ ] Email notification requirements addressed
- [ ] CSV generation requirements addressed (if applicable)
- [ ] Mobile responsiveness considered
- [ ] Loading and error states specified
- [ ] Existing patterns and utilities reused where possible

---

## Integration with Development Tools

### Django Management Commands
```bash
# Create migrations after model changes
python manage.py makemigrations {app}

# Apply migrations
python manage.py migrate

# Create superuser for testing
python manage.py createsuperuser

# Run development server
python manage.py runserver

# Run tests for specific app
python manage.py test {app}

# Run all tests
python manage.py test

# Create app if needed
python manage.py startapp {app_name}
```

### Frontend Development Commands
```bash
# Install dependencies
npm install

# Start development server
npm start

# Run tests
npm test

# Build for production
npm run build

# Type checking
npx tsc --noEmit
```

### Testing & Debugging
```bash
# Backend API testing with curl
curl -X POST http://127.0.0.1:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","password":"password"}'

# Django shell for debugging
python manage.py shell
>>> from users.models import CustomUser
>>> CustomUser.objects.all()

# Database inspection
python manage.py dbshell
```

---

## Command Recognition & Workflow Triggers

### When user says:
- **"Plan a new feature for X"** → Begin Phase 0 (Context Loading), then Phase 1 (PRD Creation)
- **"Create a fix for X"** → Begin Phase 0, then Phase 1 with fix- prefix
- **"Create the development plan"** → Begin Phase 2 (Plan Document Creation)
- **"Update the documentation tree"** → Update docs/tree.md with new entry
- **"Review existing features"** → List and summarize docs directory contents
- **"What's the status of X?"** → Read and summarize X.plan.md milestone status
- **"I'm ready to start implementing"** → Review plan checklist, confirm all docs complete
- **"Update milestone X status"** → Update status in plan.md to In Progress/Completed

### Proactive Suggestions:
After PRD creation, suggest:
- "Would you like me to create the development plan now?"
- "Should I update the docs/tree.md file?"

After Plan creation, suggest:
- "The planning phase is complete. Would you like me to help you start implementation?"
- "Shall I create the feature branch in git?"

---

## Review Checkpoints & Validation

### After PRD Creation:
1. **Pause for user review** - Don't proceed until approved
2. **Present summary:**
   - Feature name and directory
   - Affected Django apps and components
   - Estimated complexity
   - Key API endpoints
   - Major UI components
3. **Ask clarifying questions:**
   - "Should this require staff permissions?"
   - "Do we need email notifications?"
   - "Should there be CSV export?"
   - "Any specific validation rules?"

### After Plan Creation:
1. **Pause for user review** - Confirm before marking complete
2. **Present development summary:**
   - Total estimated time
   - Number of milestones and tasks
   - Backend vs frontend split
   - Key dependencies
   - Risk factors
3. **Confirm readiness:**
   - "Does the task breakdown make sense?"
   - "Are the time estimates reasonable?"
   - "Have we covered all integration points?"

### Before Starting Implementation:
1. **Verify documentation complete:**
   - PRD approved ✓
   - Plan approved ✓
   - tree.md updated ✓
2. **Suggest next steps:**
   - Create feature branch
   - Start with backend models
   - Set up test data
3. **Remind of workflow:**
   - Backend first (models → serializers → views)
   - Test API endpoints before frontend
   - Update TypeScript types
   - Build frontend components

---

## Example PRD Template (Quick Reference)

```markdown
# Product Requirements Document: [Feature Name]

## Title
[Feature Name] - [One sentence description]

## Overview
[2-3 sentences about what this feature does]

## Problem Statement
[What problem does this solve for DesiDeliver users?]

## User Stories
### As a Restaurant Owner
- I want to [action] so that [benefit]

### As a Delivery Coordinator
- I want to [action] so that [benefit]

## Functional Requirements
1. [Requirement 1]
2. [Requirement 2]

## Technical Requirements

### Backend Changes
- **Django App**: orders/products/cart/users
- **Models**: New/Modified models with fields
- **Serializers**: New/Modified serializers
- **Views**: New endpoints
- **URLs**: New routes

### Frontend Changes
- **Components**: New/Modified components in src/components/
- **Types**: TypeScript interfaces in src/types/
- **API Service**: New methods in src/services/api.ts
- **Context**: Updates to AuthContext or CartContext

### Database Schema
[Describe new tables, columns, relationships]

## API Specifications

### Endpoint Name
```
POST /api/module/action/
Authentication: JWT Required
Permissions: IsAuthenticated

Request:
{
  "field": "value"
}

Response (200):
{
  "id": 1,
  "field": "value"
}
```

## UI/UX Requirements
- Material-UI components: [List]
- User flow: [Step by step]
- Validation rules: [List]

## Success Criteria
- [ ] Functional criterion 1
- [ ] Functional criterion 2

## Security Considerations
- Authentication: [Requirements]
- Authorization: [Permissions]
- Validation: [Rules]

## Dependencies
- Existing features: [List]
- External services: [List]

## Testing Requirements
- Backend: [Test scenarios]
- Frontend: [Test scenarios]
```

---

## Example Plan Template (Quick Reference)

```markdown
# Development Plan: [Feature Name]

## Overview
[Brief description]
Reference: [PRD Document](./feat-name.prd.md)

## Project Timeline
**Total Estimated Duration**: 1 week
**Complexity**: Medium

## Milestones

### Milestone 1: Backend Models
- [ ] Status: Not Started
- Estimated Duration: 1 day

#### Tasks:
- [ ] Task 1.1: Update models in orders/models.py
  - Add Order.cancellation_reason field
  - Estimated Time: 30 mins

### Milestone 2: Backend API
- [ ] Status: Not Started
- Estimated Duration: 1 day

#### Tasks:
- [ ] Task 2.1: Create cancel order endpoint
  - File: orders/views.py
  - Endpoint: POST /api/orders/{id}/cancel/
  - Estimated Time: 2 hours

[... continue with remaining milestones ...]

## Technical Considerations
[Architecture decisions]

## Testing Strategy
[Testing approach]

## Risk Assessment
[Potential issues and mitigations]
```

---

## Final Reminders

### Always:
- ✅ Load context with learn.prompt.md first
- ✅ Review existing DesiDeliver patterns
- ✅ Follow backend-first development flow
- ✅ Include comprehensive testing requirements
- ✅ Consider both customer and staff perspectives
- ✅ Specify Material-UI components for consistency
- ✅ Include database migration steps
- ✅ Plan for email notifications where needed
- ✅ Update docs/tree.md
- ✅ Pause for user review at checkpoints

### Never:
- ❌ Skip Phase 0 (Context Loading)
- ❌ Create plan without PRD approval
- ❌ Forget to specify Django app affected
- ❌ Ignore existing authentication patterns
- ❌ Skip TypeScript interface definitions
- ❌ Forget database migration tasks
- ❌ Ignore testing requirements
- ❌ Start implementation without plan approval

---

## Success Criteria for Planning Phase

Planning is complete and successful when:
1. ✅ PRD document is comprehensive and approved
2. ✅ Plan document has detailed milestones and tasks
3. ✅ docs/tree.md is updated
4. ✅ All integration points identified
5. ✅ Time estimates are realistic
6. ✅ Testing strategy is defined
7. ✅ Risk assessment is complete
8. ✅ User has approved and is ready to implement
9. ✅ Feature branch name is decided
10. ✅ First implementation task is clear