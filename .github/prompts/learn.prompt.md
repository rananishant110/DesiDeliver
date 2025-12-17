---
mode: agent
---

# DesiDeliver Application - Complete Architecture & Learning Guide

## Mission
Analyze and comprehend the complete architecture, implementation, and functionality of DesiDeliver - a comprehensive Indian grocery supply management system for the DFW area. This prompt ensures complete understanding of both frontend (React/TypeScript) and backend (Django/Python) systems, their integration, data models, business logic, and deployment architecture.

---

## PHASE 1: Project Context & Business Understanding

### 1.1 Read Core Documentation
Analyze these documents in order to understand business requirements and project scope:

```
REQUIRED READING:
1. /docs/feat-desi-deliver-app/feat-desi-deliver-app.prd.md - Product Requirements Document
2. /docs/feat-desi-deliver-app/feat-desi-deliver-app.plan.md - Development Plan & Milestones
3. /backend/README.md - Backend technical overview
4. /docs/tree.md - Project structure reference (if exists)
```

### 1.2 Business Domain Knowledge
After reading documentation, understand:
- **Target Market**: DFW area restaurants and stores ordering Indian groceries
- **Business Model**: B2B supply platform with order-to-delivery workflow
- **Key Users**: Restaurant/Store owners (customers) and Delivery Coordinators (staff)
- **Core Value Proposition**: Streamline manual ordering process with digital catalog and automated order processing
- **Product Catalog**: 3,741+ items across 8 categories (Organic, Branded, Nonfood, Bulk, Supplies, Frozen, Mainpage, Grain Market)

---

## PHASE 2: Backend Architecture Analysis (Django)

### 2.1 Core Django Configuration
```
EXAMINE IN THIS ORDER:
1. /backend/desideliver_backend/settings.py - Django configuration, installed apps, middleware
2. /backend/desideliver_backend/urls.py - Main URL routing structure
3. /backend/manage.py - Django management commands
4. /backend/requirements.txt - Python dependencies
```

**Key Configuration Points:**
- Django 5.2.5 + Django REST Framework 3.16.1
- SQLite for development, PostgreSQL for production
- JWT authentication with djangorestframework-simplejwt
- CORS enabled via django-cors-headers
- SendGrid integration for email notifications
- Custom user model: `users.CustomUser`

### 2.2 Users App - Authentication & Authorization
```
ANALYZE SEQUENTIALLY:
1. /backend/users/models.py - CustomUser model extending AbstractUser
2. /backend/users/serializers.py - User registration, login, profile serializers
3. /backend/users/views.py - Authentication endpoints (register, login, logout, profile)
4. /backend/users/urls.py - User API routing
5. /backend/users/admin.py - Admin interface customization
```

**Key Concepts:**
- **CustomUser Model Fields**:
  - Business information: business_name, business_type (restaurant/store/catering/other)
  - Contact: phone_number, email
  - Address: address_line1, address_line2, city, state, zip_code
  - Verification: is_verified, is_active
  - Business credentials: tax_id, business_license
- **Authentication Flow**: JWT tokens (access + refresh), stored in localStorage
- **User Types**: Regular customers (is_staff=False) vs Staff (is_staff=True)

### 2.3 Products App - Catalog Management
```
ANALYZE SEQUENTIALLY:
1. /backend/products/models.py - Category and Product models
2. /backend/products/serializers.py - Product data serialization
3. /backend/products/views.py - Product listing, search, filtering endpoints
4. /backend/products/urls.py - Product API routing
5. /docs/catalog/catalog.json - Complete product catalog (3,741 items)
```

**Key Concepts:**
- **Category Model**: name, slug, description, is_active
- **Product Model Fields**:
  - Identity: item_code (unique), name, description
  - Classification: category (ForeignKey)
  - Inventory: in_stock, stock_quantity, unit (kg/lb/piece/pack)
  - Constraints: min_order_quantity
  - Metadata: brand, origin, weight, is_active
- **Search & Filtering**: By category, item_code, name, in_stock status
- **Pagination**: Supports large catalog browsing

### 2.4 Cart App - Shopping Cart Management
```
ANALYZE SEQUENTIALLY:
1. /backend/cart/models.py - Cart and CartItem models
2. /backend/cart/serializers.py - Cart serialization with nested items
3. /backend/cart/views.py - Add, update, remove cart items
4. /backend/cart/urls.py - Cart API routing
```

**Key Concepts:**
- **Cart Model**: One-to-one with user, is_active flag, timestamps
- **CartItem Model**: 
  - Unique constraint: (cart, product) - no duplicate products in cart
  - quantity field with MinValueValidator(1)
  - Methods: validate_quantity(), is_available()
- **Cart Operations**: Add, update quantity, remove item, clear cart
- **Persistence**: Cart persists across sessions for logged-in users
- **Validation**: Check product availability and min_order_quantity

### 2.5 Orders App - Order Processing & Workflow
```
ANALYZE SEQUENTIALLY:
1. /backend/orders/models.py - Order and OrderItem models
2. /backend/orders/serializers.py - Order data serialization
3. /backend/orders/views.py - Create, list, retrieve, update orders
4. /backend/orders/utils.py - CSV generation utilities
5. /backend/orders/email_service.py - Email notification system
6. /backend/orders/order_processor.py - Automated order workflow
7. /backend/orders/urls.py - Order API routing
```

**Key Concepts:**
- **Order Model**:
  - order_number: Auto-generated (format: DD{YYYYMMDD}{###})
  - Status workflow: pending → confirmed → processing → ready → delivered (or cancelled)
  - Delivery info: delivery_address, delivery_instructions, preferred_delivery_date
  - Business context: business_name, contact_person, phone_number
- **OrderItem Model**: product reference, quantity
- **CSV Generation**: CSVGenerator creates order CSV with item_code, description, quantity
- **Email Service**: 
  - Customer confirmation emails
  - Delivery coordinator notifications with CSV attachment
  - Status update notifications
  - Uses SendGrid API or Django SMTP backend
- **Order Processor**: Automated status change notifications and workflow management

### 2.6 Database Schema & Relationships
```
UNDERSTAND RELATIONSHIPS:
- CustomUser (1) → (M) Cart → (M) CartItem → (1) Product
- CustomUser (1) → (M) Order → (M) OrderItem → (1) Product
- Category (1) → (M) Product
```

**Database Indexes**: On item_code, category, is_active, order_number, customer, status, created_at

### 2.7 API Endpoint Structure
```
MEMORIZE API ROUTES:
/api/auth/
  - POST /register/ - User registration
  - POST /login/ - User login (returns JWT tokens)
  - POST /logout/ - User logout
  - GET /profile/ - Get user profile
  - PUT /profile/ - Update user profile
  - POST /password/change/ - Change password
  
/api/products/
  - GET /categories/ - List all categories
  - GET / - List products (supports ?category=, ?search=, ?page=)
  - GET /{id}/ - Get product details
  
/api/cart/
  - GET / - Get user's cart with items
  - POST /add/ - Add item to cart
  - PUT /update/{id}/ - Update cart item quantity
  - DELETE /remove/{id}/ - Remove cart item
  - POST /clear/ - Clear entire cart
  
/api/orders/
  - POST /create/ - Create order from cart
  - GET / - List user's orders
  - GET /{id}/ - Get order details
  - PATCH /{id}/status/ - Update order status (staff only)
  - GET /stats/ - Get order statistics (staff only)
  - GET /{id}/csv/ - Download order CSV
```

---

## PHASE 3: Frontend Architecture Analysis (React/TypeScript)

### 3.1 Core Frontend Setup
```
EXAMINE IN THIS ORDER:
1. /frontend/package.json - Dependencies and scripts
2. /frontend/tsconfig.json - TypeScript configuration
3. /frontend/src/config.ts - Application configuration
4. /frontend/src/index.tsx - React app initialization
5. /frontend/src/App.tsx - Main application component
```

**Key Dependencies:**
- React 19.1.1 + React DOM
- TypeScript 4.9.5
- Material-UI (@mui/material 7.3.1) - UI component library
- Axios 1.11.0 - HTTP client
- React Router DOM 7.8.2 - Client-side routing
- date-fns 4.1.0 - Date manipulation

### 3.2 Type Definitions
```
ANALYZE:
/frontend/src/types/index.ts - Complete TypeScript interfaces
```

**Key Types:**
- `User`: Complete user profile with business information
- `Product`: Product catalog item with category
- `Category`: Product categorization
- `CartItem`: Cart item with product reference and quantity
- `Cart`: User's shopping cart with items array
- `Order`: Complete order with customer, items, status, delivery info
- `OrderItem`: Order line item
- `LoginCredentials`, `RegisterData`, `CreateOrderData`: Form data types
- `AuthResponse`, `ApiResponse`, `PaginatedResponse`: API response types

### 3.3 API Service Layer
```
ANALYZE:
1. /frontend/src/services/api.ts - Axios instance and API methods
```

**Key Concepts:**
- **Axios Configuration**: Base URL (default: http://127.0.0.1:8000/api)
- **Request Interceptor**: Automatically adds JWT token to Authorization header
- **Response Interceptor**: Handles token refresh on 401 errors
- **API Modules**:
  - `authAPI`: register, login, logout, getProfile, updateProfile
  - `productsAPI`: getProducts, getProduct, getCategories, searchProducts
  - `cartAPI`: getCart, addToCart, updateCartItem, removeCartItem, clearCart
  - `ordersAPI`: createOrder, getOrders, getOrder, updateOrderStatus, getOrderStats

### 3.4 State Management - Contexts
```
ANALYZE SEQUENTIALLY:
1. /frontend/src/contexts/AuthContext.tsx - Authentication state management
2. /frontend/src/contexts/CartContext.tsx - Shopping cart state management
```

**AuthContext:**
- **State**: user, isAuthenticated, isLoading, error
- **Actions**: login, register, logout, updateProfile, clearError
- **Persistence**: Stores tokens and user in localStorage
- **Auto-login**: Checks localStorage on app load

**CartContext:**
- **State**: cart, items, totalItems, isLoading, error
- **Actions**: addToCart, updateQuantity, removeFromCart, clearCart, refreshCart
- **Real-time**: Syncs with backend on every cart operation

### 3.5 Component Architecture
```
ANALYZE BY FEATURE MODULE:

/frontend/src/components/auth/
  - LoginForm.tsx - User authentication UI

/frontend/src/components/common/
  - Layout.tsx - Application shell with navigation
  - Dashboard.tsx - Main dashboard with feature navigation

/frontend/src/components/catalog/
  - ProductCatalog.tsx - Main catalog container
  - ProductGrid.tsx - Product list display
  - SearchFilters.tsx - Category and search filters
  - CategoryNav.tsx - Category navigation
  - Pagination.tsx - Page navigation

/frontend/src/components/cart/
  - CartPage.tsx - Full cart view
  - CartSidebar.tsx - Slide-out cart
  - CartItem.tsx - Individual cart item component
  - CartBadge.tsx - Cart icon with item count

/frontend/src/components/orders/
  - OrdersPage.tsx - Order history container
  - CheckoutForm.tsx - Order creation form
  - OrderDetail.tsx - Individual order view
  - OrderHistory.tsx - List of past orders

/frontend/src/components/staff/
  - StaffDashboard.tsx - Staff-only order management interface
```

**UI Framework**: Material-UI components (Button, TextField, Card, Grid, Dialog, etc.)

### 3.6 Routing & Navigation
```
UNDERSTAND NAVIGATION FLOW:
- State-based routing (no React Router in current implementation)
- Routes: 'dashboard', 'catalog', 'cart', 'orders', 'staff'
- Navigation via Layout component
- Protected routes via AuthContext isAuthenticated check
```

### 3.7 Utility Functions
```
ANALYZE:
1. /frontend/src/utils/index.ts - General utilities
2. /frontend/src/utils/searchUtils.ts - Search and filtering helpers
3. /frontend/src/hooks/useApi.ts - Custom API hooks
```

---

## PHASE 4: Integration & Data Flow

### 4.1 Authentication Flow
```
TRACE COMPLETE FLOW:
1. User enters credentials in LoginForm.tsx
2. Component calls authContext.login()
3. AuthContext calls authAPI.login()
4. API service sends POST /api/auth/login/
5. Backend validates credentials, returns JWT tokens + user data
6. Frontend stores tokens in localStorage
7. AuthContext updates state: isAuthenticated = true, user = userData
8. App.tsx renders authenticated view
9. All subsequent API calls include Authorization: Bearer {token} header
```

### 4.2 Product Browsing Flow
```
TRACE COMPLETE FLOW:
1. User navigates to catalog
2. ProductCatalog.tsx mounts, calls productsAPI.getProducts()
3. API sends GET /api/products/ with filters/pagination
4. Backend queries Product model with filters
5. ProductSerializer formats data with nested Category
6. Frontend receives paginated product list
7. ProductGrid.tsx renders product cards
8. User can filter by category, search by name, paginate
```

### 4.3 Shopping Cart Flow
```
TRACE COMPLETE FLOW:
1. User clicks "Add to Cart" on product
2. Component calls cartContext.addToCart(productId, quantity)
3. CartContext calls cartAPI.addToCart()
4. API sends POST /api/cart/add/ with {product_id, quantity}
5. Backend creates/updates CartItem in user's Cart
6. CartSerializer returns updated cart with all items
7. CartContext updates state with new cart
8. CartBadge.tsx shows updated item count
9. Cart persists across sessions (stored in database)
```

### 4.4 Order Creation Flow
```
TRACE COMPLETE FLOW:
1. User reviews cart, clicks "Checkout"
2. CheckoutForm.tsx displays order form
3. User enters delivery info, preferred date
4. Form calls ordersAPI.createOrder(orderData)
5. API sends POST /api/orders/create/
6. Backend validates data, creates Order and OrderItems from cart
7. OrderProcessor generates CSV file
8. EmailService sends:
   - Confirmation email to customer
   - Notification + CSV to delivery coordinator
9. Cart is cleared and marked inactive
10. Frontend shows order confirmation with order_number
11. Order appears in OrderHistory
```

### 4.5 Staff Order Management Flow
```
TRACE COMPLETE FLOW:
1. Staff user logs in (is_staff = true)
2. Accesses StaffDashboard
3. Views all pending orders via ordersAPI.getOrders()
4. Can update order status: pending → confirmed → processing → ready → delivered
5. Status update calls ordersAPI.updateOrderStatus()
6. Backend OrderProcessor sends notifications on status change
7. Customer receives email about status update
8. Staff can download order CSV for delivery coordination
```

---

## PHASE 5: Advanced Features & Implementation Details

### 5.1 CSV Generation System
```
UNDERSTAND:
- Location: /backend/orders/utils.py
- Purpose: Generate delivery coordination CSV files
- Format: item_code, description, quantity
- Triggered: On order creation and via download endpoint
- Usage: Delivery coordinators import into logistics system
```

### 5.2 Email Notification System
```
UNDERSTAND:
- Location: /backend/orders/email_service.py
- Providers: SendGrid API (production) or Django SMTP (development/fallback)
- Email Types:
  1. Order confirmation (customer) - HTML formatted with order details
  2. Delivery coordinator notification - Includes CSV attachment
  3. Order status updates - Sent on status changes
  4. Delivery ready notification - Special notification when order ready
- Templates: HTML emails with order details, business info, items list
- Error Handling: Emails failures don't block order creation
```

### 5.3 Order Processing Workflow
```
UNDERSTAND:
- Location: /backend/orders/order_processor.py
- Purpose: Automated order lifecycle management
- Status Transitions:
  pending → confirmed (Order accepted)
  confirmed → processing (Preparing order)
  processing → ready (Ready for pickup/delivery)
  ready → delivered (Order completed)
  Any → cancelled (Order cancellation)
- Notifications: Automatic emails on each status change
- Validation: Status change validation (e.g., can't cancel delivered orders)
```

### 5.4 Search & Filtering Implementation
```
UNDERSTAND BACKEND:
- Django filters via django-filters
- Search fields: product name, item_code, description
- Filter fields: category, in_stock, is_active
- Case-insensitive search
- Efficient queries with select_related('category')

UNDERSTAND FRONTEND:
- Real-time search as user types
- Category dropdown filtering
- Combined search + category filter
- Results update without page reload
```

### 5.5 Pagination System
```
UNDERSTAND:
- Backend: Django REST Framework pagination
- Default page size: 20 items (configurable)
- Response format: {count, next, previous, results}
- Frontend: Pagination.tsx component with page navigation
- Efficient: Only loads visible page data
```

### 5.6 Security Implementation
```
UNDERSTAND:
- JWT Authentication: Access tokens (short-lived) + Refresh tokens (long-lived)
- Token Storage: localStorage (consider httpOnly cookies for production)
- CORS Configuration: Restricts API access to allowed origins
- Password Validation: Django's built-in validators (length, complexity)
- Permission Classes: IsAuthenticated for protected endpoints
- Input Validation: Django serializers validate all input
- SQL Injection Protection: Django ORM parameterized queries
- XSS Protection: React auto-escapes rendered content
```

---

## PHASE 6: Deployment & Environment Configuration

### 6.1 Backend Environment Setup
```
UNDERSTAND:
1. Virtual environment: python -m venv venv
2. Install dependencies: pip install -r requirements.txt
3. Database migrations: python manage.py migrate
4. Create superuser: python manage.py createsuperuser
5. Run server: python manage.py runserver
6. Admin panel: http://127.0.0.1:8000/admin/
```

**Environment Variables (Production):**
- SECRET_KEY: Django secret key
- DEBUG: Set to False
- ALLOWED_HOSTS: Production domains
- DATABASE_URL: PostgreSQL connection string
- SENDGRID_API_KEY: Email service API key
- DELIVERY_COORDINATOR_EMAIL: Staff notification email
- CORS_ALLOWED_ORIGINS: Frontend URLs

### 6.2 Frontend Environment Setup
```
UNDERSTAND:
1. Install dependencies: npm install
2. Development server: npm start (http://localhost:3000)
3. Production build: npm run build
4. Environment variables: Create .env file
   - REACT_APP_API_URL: Backend API URL
   - REACT_APP_ENV: development/production
```

### 6.3 Production Deployment
```
UNDERSTAND:
- Backend: Heroku, AWS, or Railway (Django + PostgreSQL)
- Frontend: Vercel or Netlify (static React build)
- Database: PostgreSQL (managed service)
- Email: SendGrid API (transactional emails)
- Static Files: AWS S3 or CDN (production)
- Monitoring: Application logging and error tracking
```

---

## PHASE 7: Testing & Quality Assurance

### 7.1 Backend Testing
```
FILES TO EXAMINE:
/backend/users/tests.py
/backend/products/tests.py
/backend/cart/tests.py
/backend/orders/tests.py
```

**Test Coverage:**
- Model validation and methods
- API endpoint responses
- Authentication and permissions
- Business logic (order creation, cart management)
- Email sending (mocked)

### 7.2 Frontend Testing
```
FILES TO EXAMINE:
/frontend/src/setupTests.ts
/frontend/src/App.test.tsx
```

**Test Libraries:**
- Jest (test runner)
- React Testing Library (component testing)
- Mock Service Worker (API mocking)

### 7.3 Manual Testing Scripts
```
EXAMINE:
/backend/test_auth.py - Authentication flow testing
/backend/test_email.py - Email system testing
/backend/test_user_data.py - User data verification
/backend/check_products.py - Product catalog validation
```

---

## PHASE 8: Development Workflow & Best Practices

### 8.1 Code Organization Principles
```
UNDERSTAND:
- Separation of Concerns: Models, Serializers, Views, Utilities
- DRY Principle: Reusable components and utilities
- API Layer: Centralized API service in frontend
- State Management: Context API for global state
- Type Safety: TypeScript interfaces for all data structures
```

### 8.2 Django Best Practices Observed
```
- Custom User Model: Extended AbstractUser early in project
- App-based Architecture: Modular apps (users, products, cart, orders)
- Serializers: Consistent data validation and transformation
- Class-based Views: Organized and reusable view classes
- Admin Interface: Customized admin for all models
- Indexes: Database indexes on frequently queried fields
```

### 8.3 React Best Practices Observed
```
- Functional Components: All components use hooks
- Context API: Global state without Redux complexity
- Type Safety: Full TypeScript usage
- Component Composition: Small, reusable components
- Material-UI: Consistent design system
- Error Handling: Try-catch blocks and error state
```

---

## PHASE 9: Key Features & User Journeys

### 9.1 Restaurant Owner Journey
```
1. Registration → Create account with business information
2. Login → Authenticate and access dashboard
3. Browse Catalog → Search 3,741+ products across 8 categories
4. Add to Cart → Build order with multiple items
5. Review Cart → Modify quantities, remove items
6. Checkout → Enter delivery details and submit order
7. Confirmation → Receive email confirmation with order number
8. Track Orders → View order history and status
9. Reorder → Use past orders to quickly reorder
```

### 9.2 Delivery Coordinator Journey
```
1. Login → Staff access to system
2. View Pending Orders → See all new orders
3. Review Order Details → Customer info, items, delivery address
4. Download CSV → Import into logistics system
5. Update Status → confirmed → processing → ready → delivered
6. Customer Notifications → System automatically emails customer
7. Order Analytics → View order statistics and trends
```

---

## PHASE 10: Validation Checklist

After completing all phases, verify understanding by answering:

### Architecture Understanding
- ✅ Can you explain the Django app structure and why each app exists?
- ✅ Can you describe the React component hierarchy?
- ✅ Can you draw the database schema with relationships?
- ✅ Can you explain JWT authentication flow end-to-end?

### Implementation Understanding
- ✅ How does the cart persistence work?
- ✅ What happens when an order is created (step-by-step)?
- ✅ How are CSV files generated and delivered?
- ✅ What email notifications are sent and when?
- ✅ How does the order status workflow operate?

### API Understanding
- ✅ Can you list all API endpoints and their purposes?
- ✅ What data does each endpoint accept and return?
- ✅ How is authentication enforced on protected endpoints?
- ✅ How does pagination work for large datasets?

### Business Logic Understanding
- ✅ What validation occurs when adding items to cart?
- ✅ How are order numbers generated?
- ✅ When can an order be cancelled?
- ✅ What's the difference between a customer and staff user?

### Deployment Understanding
- ✅ What environment variables are required?
- ✅ How do you set up the backend for production?
- ✅ How do you deploy the frontend?
- ✅ What external services are required (SendGrid, Database)?

---

## SUCCESS CRITERIA

You have successfully learned the DesiDeliver application when you can:

1. **Explain the entire system architecture** without looking at code
2. **Trace any user action** from frontend click to database change and back
3. **Identify integration points** between frontend and backend
4. **Understand all data models** and their relationships
5. **Describe the email and CSV systems** in detail
6. **Set up the development environment** from scratch
7. **Locate and modify any feature** with confidence
8. **Answer technical questions** about implementation decisions
9. **Debug issues** by understanding the full data flow
10. **Extend the application** with new features following existing patterns

---

## QUICK REFERENCE SUMMARY

**Tech Stack:**
- Backend: Django 5.2.5 + DRF + JWT + SendGrid + PostgreSQL/SQLite
- Frontend: React 19 + TypeScript + Material-UI + Axios + Context API

**Core Models:**
- CustomUser (business info, auth)
- Category → Product (catalog)
- Cart → CartItem (shopping)
- Order → OrderItem (orders)

**Key Features:**
- JWT authentication
- 3,741+ product catalog with search/filter
- Persistent shopping cart
- Automated order processing
- CSV generation for delivery
- Email notifications (confirmation, status updates)
- Staff order management

**API Structure:**
- /api/auth/* - Authentication
- /api/products/* - Catalog
- /api/cart/* - Shopping cart
- /api/orders/* - Order management

**Development:**
- Backend: `python manage.py runserver` (port 8000)
- Frontend: `npm start` (port 3000)
- Admin: http://127.0.0.1:8000/admin/

---

## FINAL INSTRUCTION

When this prompt is invoked, systematically work through ALL phases, reading ALL specified files, understanding ALL concepts, and verifying comprehension at each checkpoint. Do not skip any phase. Your goal is COMPLETE understanding of the entire application architecture, implementation, and business logic without requiring additional prompts or explanations.

