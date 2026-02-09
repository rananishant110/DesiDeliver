# DesiDeliver - GitHub Copilot Instructions

## Project Overview
DesiDeliver is a B2B food and grocery delivery platform connecting restaurants and stores with suppliers. The system consists of a Django REST Framework backend and a React TypeScript frontend with Material-UI.

## Tech Stack

### Backend
- **Framework**: Django 4.x with Django REST Framework
- **Database**: PostgreSQL (production), SQLite (development)
- **Task Queue**: Celery with Redis
- **Authentication**: JWT-based authentication
- **Email**: Django email backend with templates
- **API**: RESTful API with DRF serializers and viewsets

### Frontend
- **Framework**: React 19 with TypeScript
- **UI Library**: Material-UI v7
- **Routing**: React Router v7
- **State Management**: React Context API
- **HTTP Client**: Axios
- **Animation**: Framer Motion
- **Styling**: Emotion (CSS-in-JS)
- **Maps**: Leaflet/React-Leaflet for delivery tracking

## Code Standards

### Backend (Python/Django)
1. **File Structure**:
   - Models in `models.py` with clear field definitions and validators
   - Serializers in `serializers.py` using DRF serializers
   - Views in `views.py` using ViewSets or APIView
   - URLs in `urls.py` with clear routing patterns
   - Business logic in separate utility files (`utils.py`, `services.py`)
   - Background tasks in `tasks.py` using Celery

2. **Naming Conventions**:
   - Use snake_case for variables, functions, and file names
   - Use PascalCase for class names
   - Prefix boolean fields with `is_` or `has_`
   - Use descriptive model names (Order, Product, DeliveryTracking)

3. **Models**:
   - Always include `created_at` and `updated_at` fields
   - Add indexes for frequently queried fields
   - Use `related_name` for reverse relationships
   - Add `help_text` for complex fields
   - Use choices for status fields
   - Include `__str__` method for readable representations

4. **Serializers**:
   - Use nested serializers for related objects
   - Add custom validation in `validate_*` methods
   - Use `Meta` class for model serializer configuration
   - Include read-only fields appropriately

5. **Views**:
   - Use ViewSets for standard CRUD operations
   - Use APIView for custom endpoints
   - Add permission classes for authentication/authorization
   - Handle exceptions with proper error responses
   - Use pagination for list endpoints

6. **Security**:
   - Use JWT for API authentication
   - Validate all user inputs
   - Use Django permissions and custom permission classes
   - Never expose sensitive data in API responses

### Frontend (React/TypeScript)
1. **File Structure**:
   - Components in `src/components/` organized by feature
   - Types in `src/types/index.ts`
   - API services in `src/services/`
   - Context providers in `src/contexts/`
   - Custom hooks in `src/hooks/`
   - Theme configuration in `src/theme/`
   - Utilities in `src/utils/`

2. **Naming Conventions**:
   - Use PascalCase for component names and files
   - Use camelCase for variables, functions, and props
   - Use UPPER_SNAKE_CASE for constants
   - Prefix custom hooks with `use`
   - Prefix interfaces with `I` only when necessary

3. **Components**:
   - Use functional components with hooks
   - Extract reusable logic into custom hooks
   - Keep components focused and single-responsibility
   - Use TypeScript interfaces for props
   - Add JSDoc comments for complex components

4. **State Management**:
   - Use Context API for global state (Auth, Cart, Theme)
   - Use local state for component-specific data
   - Prefer controlled components for forms
   - Use useReducer for complex state logic

5. **Styling**:
   - Use Material-UI theme system
   - Use sx prop for component-specific styles
   - Define reusable theme colors in `theme/palette.ts`
   - Use semantic color system from `theme/semanticColors.ts`
   - Avoid inline styles unless dynamic

6. **API Integration**:
   - All API calls through services in `src/services/api.ts`
   - Use axios interceptors for auth tokens
   - Handle loading and error states
   - Type all API responses with interfaces

7. **TypeScript**:
   - Always define types for props, state, and API responses
   - Use interfaces for object shapes
   - Use type aliases for unions and intersections
   - Avoid `any` type - use `unknown` if needed
   - Enable strict mode

## Feature Development Guidelines

### Adding New Features
1. **Backend**:
   - Create/update models with migrations
   - Create serializers for API data transformation
   - Implement views with proper permissions
   - Add URL routes
   - Write tests for business logic
   - Update admin interface if needed

2. **Frontend**:
   - Define TypeScript types/interfaces
   - Create API service methods
   - Build UI components following design system
   - Add routing if needed
   - Handle loading, error, and empty states
   - Ensure responsive design

### Delivery Tracking Feature
When implementing delivery tracking:
- Use location coordinates (latitude/longitude)
- Track delivery status with timestamps
- Assign delivery personnel to orders
- Show real-time location updates on map
- Send notifications for status changes
- Allow photo uploads for proof of delivery
- Calculate estimated delivery times
- Track delivery route history

## Database Conventions
- Use meaningful table/model names
- Add indexes for foreign keys and frequently queried fields
- Use `TextField` for long text, `CharField` for short text
- Use `DecimalField` for currency
- Use `JSONField` for flexible data structures
- Always add `on_delete` for ForeignKey fields

## API Design
- Use RESTful conventions
- Version APIs if needed (/api/v1/)
- Return consistent response formats
- Use proper HTTP status codes
- Include pagination metadata
- Add filtering and search capabilities
- Document endpoints with docstrings

## Error Handling
- Backend: Return appropriate HTTP status codes with error messages
- Frontend: Show user-friendly error messages
- Log errors for debugging
- Handle network failures gracefully
- Validate data on both frontend and backend

## Performance
- Use select_related and prefetch_related for query optimization
- Implement pagination for large datasets
- Use React.memo for expensive components
- Lazy load images and heavy components
- Use WebSocket or polling for real-time updates
- Cache frequently accessed data

## Testing
- Write unit tests for business logic
- Test API endpoints with DRF test client
- Test React components with React Testing Library
- Test edge cases and error scenarios

## Git Workflow
- Use feature branches
- Write descriptive commit messages
- Keep commits focused and atomic
- Review changes before committing

## Documentation
- Add docstrings to Python functions/classes
- Add JSDoc comments to complex TypeScript functions
- Document API endpoints
- Update README for major features
- Keep this Copilot instructions file updated

## Common Patterns

### Django Model Example
```python
class DeliveryTracking(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='tracking')
    driver = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='deliveries')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    current_latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True)
    current_longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        indexes = [models.Index(fields=['order', 'status'])]
```

### React Component Example
```typescript
interface DeliveryMapProps {
  orderId: number;
  tracking: DeliveryTracking;
}

const DeliveryMap: React.FC<DeliveryMapProps> = ({ orderId, tracking }) => {
  // Component implementation
};
```

### API Service Example
```typescript
export const trackingService = {
  getTracking: (orderId: number) => 
    api.get<DeliveryTracking>(`/api/tracking/${orderId}/`),
  
  updateLocation: (trackingId: number, location: LocationUpdate) =>
    api.patch(`/api/tracking/${trackingId}/location/`, location),
};
```

## Specific Instructions for Copilot

When writing code for DesiDeliver:
1. Always use TypeScript for frontend code
2. Follow the existing project structure
3. Use Material-UI components and theme system
4. Implement proper error handling and loading states
5. Add type definitions for all data structures
6. Use Django best practices for backend
7. Include proper authentication checks
8. Write clean, maintainable, and documented code
9. Consider mobile responsiveness
10. Follow REST API conventions
