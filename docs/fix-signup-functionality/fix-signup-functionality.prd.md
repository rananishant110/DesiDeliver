# Product Requirements Document: Fix Signup Functionality

## Title
Fix Signup Functionality - Implement Registration Form and Navigation

## Overview
The signup button on the login page currently does nothing. Users cannot register for new accounts even though the backend registration endpoint exists. This fix will create a registration form component and wire up the navigation to enable new user registration.

## Problem Statement
Restaurant owners and store owners visiting DesiDeliver cannot create new accounts because:
1. No registration form component exists in the frontend
2. The "Sign up here" button on the login page has no navigation logic
3. There is no route configured for the registration page in App.tsx
4. The existing backend `/api/auth/register/` endpoint is functional but unreachable from the UI

This prevents new customers from onboarding to the platform, blocking business growth and user acquisition.

## User Stories

### As a Restaurant Owner
- I want to click the "Sign up here" button on the login page so that I can access the registration form
- I want to fill out a registration form with my business details so that I can create an account
- I want to see clear validation messages so that I know what information is required
- I want to be automatically logged in after registration so that I can start browsing products immediately

### As a Store Owner
- I want to register my business on DesiDeliver so that I can order Indian grocery supplies
- I want the registration process to be simple and clear so that I can complete it quickly

### As a System Administrator
- I want new users to provide complete business information during registration so that we can verify legitimate businesses
- I want registration data to be validated so that we maintain data quality

## Functional Requirements

1. **Registration Form Component**
   - Must include all fields required by the backend RegisterData interface
   - Form fields:
     - Username (unique, required)
     - Email (valid email format, required)
     - Password (minimum 8 characters, required)
     - Confirm Password (must match password, required)
     - First Name (required)
     - Last Name (required)
     - Business Name (required)
     - Business Type (dropdown: restaurant/store/other, required)
     - Phone Number (required, format validation)
     - Address Line 1 (required)
     - Address Line 2 (optional)
     - City (required)
     - State (required)
     - ZIP Code (required, format validation)

2. **Form Validation**
   - Client-side validation for all required fields
   - Email format validation
   - Password strength validation (minimum 8 characters)
   - Password confirmation matching
   - Phone number format validation (US format)
   - ZIP code format validation (5 or 9 digits)
   - Real-time validation feedback

3. **User Experience**
   - Clear error messages for validation failures
   - Loading state during registration submission
   - Success message on successful registration
   - Automatic redirect to dashboard after successful registration
   - "Already have an account? Sign in" link to return to login

4. **Navigation**
   - Login page "Sign up here" button navigates to `/register`
   - Registration page "Sign in" link navigates to `/login`
   - Authenticated users redirected away from registration page

## Technical Requirements

### Backend Changes
- **Django App**: users (already exists)
- **Endpoint**: `/api/auth/register/` (already implemented)
- **No backend changes required** - endpoint is functional

### Frontend Changes

#### New Components
- **File**: `src/components/auth/RegistrationForm.tsx`
  - Registration form component with Material-UI
  - Uses AuthContext.register() method
  - Form validation and error handling
  - Loading states and success/error alerts

#### Component Updates
- **File**: `src/components/auth/LoginForm.tsx`
  - Update "Sign up here" button onClick to navigate to `/register` using react-router-dom's `useNavigate()`

#### Routing Updates
- **File**: `src/App.tsx`
  - Add new route: `/register` → `<RegistrationForm />`
  - Make it a public route (accessible when not authenticated)
  - Redirect authenticated users away from registration page

#### Type Definitions
- **File**: `src/types/index.ts`
  - RegisterData interface already exists ✅
  - No changes needed

#### API Service
- **File**: `src/services/api.ts`
  - Check if `authAPI.register()` method exists
  - Verify it calls POST `/api/auth/register/`

#### Context
- **File**: `src/contexts/AuthContext.tsx`
  - Verify `register()` function exists and works correctly

### Database Changes
- No database changes required (User model already exists)

## API Specifications

### Registration Endpoint (Already Exists)
```
POST /api/auth/register/
Authentication: Not Required (Public endpoint)
Permissions: AllowAny

Request Body:
{
  "username": "johndoe123",
  "email": "john@restaurant.com",
  "password": "SecurePass123!",
  "password_confirm": "SecurePass123!",
  "first_name": "John",
  "last_name": "Doe",
  "business_name": "John's Indian Restaurant",
  "business_type": "restaurant",
  "phone_number": "469-555-0123",
  "address_line1": "123 Main Street",
  "address_line2": "Suite 100",
  "city": "Dallas",
  "state": "TX",
  "zip_code": "75001"
}

Response (201 Created):
{
  "message": "User registered successfully",
  "user": {
    "id": 1,
    "username": "johndoe123",
    "email": "john@restaurant.com",
    "first_name": "John",
    "last_name": "Doe",
    "business_name": "John's Indian Restaurant",
    "business_type": "restaurant",
    "is_verified": false,
    "is_staff": false
  },
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}

Response (400 Bad Request):
{
  "username": ["A user with that username already exists."],
  "email": ["This field must be a valid email address."],
  "password": ["This password is too short. It must contain at least 8 characters."]
}
```

## UI/UX Requirements

### Material-UI Components
- **Form Layout**: `Paper` component for card-style form
- **Text Inputs**: `TextField` components with proper labels
- **Dropdown**: `Select` component for business type
- **Buttons**: `Button` component (primary variant for submit)
- **Alerts**: `Alert` component for errors and success messages
- **Loading**: `CircularProgress` for loading state

### Registration Form Layout
1. **Header Section**
   - Title: "Create Your DesiDeliver Account"
   - Subtitle: "Join us to start ordering Indian groceries"

2. **Form Sections** (organized for clarity)
   - **Account Information**
     - Username
     - Email
     - Password
     - Confirm Password
   
   - **Personal Information**
     - First Name
     - Last Name
   
   - **Business Information**
     - Business Name
     - Business Type (dropdown)
     - Phone Number
   
   - **Address Information**
     - Address Line 1
     - Address Line 2
     - City, State, ZIP Code (in a row)

3. **Action Buttons**
   - "Create Account" button (full-width, disabled during loading)
   - "Already have an account? Sign in" link

### User Flow
1. User visits `/login`
2. User clicks "Sign up here" button
3. Browser navigates to `/register`
4. User fills out registration form
5. User clicks "Create Account"
6. Loading spinner appears, button disabled
7. On success:
   - Success alert shown briefly
   - User automatically logged in (tokens stored)
   - Redirect to dashboard (`/`)
8. On error:
   - Error alert shown with specific messages
   - Form remains editable
   - User can correct errors and resubmit

### Form Validation Rules
- **Username**: Required, 3-150 characters, alphanumeric and underscores
- **Email**: Required, valid email format
- **Password**: Required, minimum 8 characters
- **Confirm Password**: Required, must match password
- **First Name**: Required
- **Last Name**: Required
- **Business Name**: Required
- **Business Type**: Required, must be one of: restaurant, store, other
- **Phone Number**: Required, US format (xxx-xxx-xxxx or similar)
- **Address Line 1**: Required
- **City**: Required
- **State**: Required, 2-letter state code
- **ZIP Code**: Required, 5 or 9 digits (xxxxx or xxxxx-xxxx)

### Error Handling
- Display backend validation errors inline below respective fields
- Display general errors in an Alert at the top of the form
- Clear errors when user starts editing a field
- Maintain form data if submission fails (don't reset form)

## Success Criteria

### Functional
- [x] Backend `/api/auth/register/` endpoint exists and works ✅
- [x] User can navigate from login page to registration page ✅
- [x] User can fill out complete registration form ✅
- [x] Form validates all inputs on client side ✅
- [x] Form submits data to backend API ✅
- [x] Success response logs user in automatically ✅
- [x] User is redirected to dashboard after successful registration ✅
- [x] Error responses show clear error messages ✅
- [x] User can navigate back to login page from registration page ✅

### User Experience
- [x] Form is visually consistent with login form design ✅
- [x] Form is mobile responsive ✅
- [x] Loading states provide clear feedback ✅
- [x] Validation errors are clear and helpful ✅
- [x] Form layout is organized and easy to understand ✅

## Security Considerations

### Authentication
- Registration endpoint is public (no JWT required)
- After successful registration, tokens are stored securely (handled by AuthContext)

### Authorization/Permissions
- No special permissions needed (public endpoint)

### Input Validation
- **Client-side**: TypeScript interfaces enforce type safety
- **Server-side**: Django serializer validates all fields (already implemented)
- Email uniqueness enforced by backend
- Username uniqueness enforced by backend

### XSS Prevention
- React automatically escapes rendered content
- No dangerouslySetInnerHTML used

### CSRF Protection
- Not required for JWT-based authentication
- Backend uses JWT tokens, not session cookies

## Constraints & Assumptions

### Technical Limitations
- Backend registration endpoint already exists and is functional
- AuthContext already has register() method implemented
- RegisterData TypeScript interface already defined

### Business Rules
- New users start as unverified (`is_verified: false`)
- New users are not staff by default (`is_staff: false`)
- Business verification happens after registration (manual admin process)

### Dependencies
- Existing AuthContext.register() method must work correctly
- Backend endpoint must return JWT tokens on successful registration
- React Router for navigation

## Dependencies

### Existing Features
- AuthContext with register() method
- Backend User model and registration endpoint
- JWT authentication system
- Material-UI theme and components

### External Services
- None required for this fix

### Third-party Libraries
- react-router-dom: useNavigate hook for navigation
- Material-UI: Form components
- Axios: HTTP requests (via authAPI)

## Testing Requirements

### Backend Tests
- [x] Verify `/api/auth/register/` endpoint accepts valid data ✅
- [x] Verify endpoint rejects invalid data (duplicate username, invalid email, etc.) ✅
- [x] Verify endpoint returns JWT tokens on success ✅
- [x] Test password confirmation validation ✅

### Frontend Tests
- [x] Test RegistrationForm component renders correctly ✅
- [x] Test form validation (required fields, email format, password match, etc.) ✅
- [x] Test successful registration flow (API call, token storage, redirect) ✅
- [x] Test error handling (display backend errors) ✅
- [x] Test navigation from login to register and back ✅
- [x] Test that authenticated users cannot access `/register` ✅

### Manual Testing Scenarios
1. **Happy Path**
   - Navigate to `/login`
   - Click "Sign up here"
   - Fill out complete registration form with valid data
   - Submit form
   - Verify success message
   - Verify redirect to dashboard
   - Verify user is logged in

2. **Validation Errors**
   - Try submitting with empty required fields
   - Try mismatched passwords
   - Try invalid email format
   - Try invalid phone number format
   - Try invalid ZIP code
   - Verify inline error messages

3. **Backend Errors**
   - Try registering with existing username
   - Try registering with existing email
   - Verify backend error messages display correctly

4. **Navigation**
   - Verify "Sign up here" button on login page works
   - Verify "Sign in" link on registration page works
   - Verify authenticated users redirected from `/register`

5. **Mobile Responsiveness**
   - Test form on mobile viewport
   - Verify all fields accessible and usable
   - Verify buttons are tappable
