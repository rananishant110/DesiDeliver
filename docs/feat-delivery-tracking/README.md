# Delivery Tracking Management System

## Overview
The Delivery Tracking Management System is a comprehensive feature for DesiDeliver that enables real-time tracking of deliveries with interactive maps, driver management, and customer feedback.

## Features

### Backend (Django)
- **Delivery Personnel Management**: Track drivers, vehicles, and performance metrics
- **Real-time Location Tracking**: Store and update driver locations in real-time
- **Delivery Status Management**: Track delivery progress through various stages
- **Route History**: Record complete delivery routes for analysis
- **Proof of Delivery**: Support for photos and signatures
- **Customer Feedback**: Rating and review system for deliveries
- **Performance Metrics**: Track driver ratings, delivery counts, and success rates

### Frontend (React/TypeScript)
- **Interactive Map View**: Leaflet-based maps showing pickup, delivery, and driver locations
- **Real-time Updates**: Auto-refresh delivery status every 30 seconds
- **Customer Tracking**: User-friendly interface for customers to track their orders
- **Driver Management Dashboard**: Staff interface to manage delivery personnel
- **Delivery Dashboard**: Overview of all active and completed deliveries
- **Feedback System**: Allow customers to rate and review deliveries

## Installation

### Backend Setup

1. **Install the delivery app** (already added to settings):
```python
# settings.py
INSTALLED_APPS = [
    # ... other apps
    'delivery',
]
```

2. **Run migrations**:
```bash
cd backend
python manage.py makemigrations delivery
python manage.py migrate
```

3. **Create a superuser** (if not already created):
```bash
python manage.py createsuperuser
```

4. **Add to URLs** (already configured):
```python
# urls.py
urlpatterns = [
    # ... other patterns
    path('api/delivery/', include('delivery.urls')),
]
```

### Frontend Setup

1. **Install dependencies**:
```bash
cd DesiDeliver-frontend
npm install
```

The following packages are now included:
- `leaflet` - Map library
- `react-leaflet` - React bindings for Leaflet
- `@types/leaflet` - TypeScript types for Leaflet

2. **Import Leaflet CSS** (already done in `index.tsx`):
```typescript
import 'leaflet/dist/leaflet.css';
import './styles/map.css';
```

## API Endpoints

### Delivery Personnel
- `GET /api/delivery/personnel/` - List all delivery personnel
- `GET /api/delivery/personnel/{id}/` - Get personnel details
- `POST /api/delivery/personnel/` - Create new personnel
- `PATCH /api/delivery/personnel/{id}/` - Update personnel
- `PATCH /api/delivery/personnel/{id}/update_location/` - Update driver location
- `PATCH /api/delivery/personnel/{id}/update_status/` - Update driver status
- `GET /api/delivery/personnel/{id}/current_delivery/` - Get active delivery

### Delivery Tracking
- `GET /api/delivery/tracking/` - List all delivery trackings
- `GET /api/delivery/tracking/{id}/` - Get tracking details
- `POST /api/delivery/tracking/` - Create delivery tracking
- `PATCH /api/delivery/tracking/{id}/` - Update tracking
- `PATCH /api/delivery/tracking/{id}/update_location/` - Update delivery location
- `PATCH /api/delivery/tracking/{id}/update_status/` - Update delivery status
- `POST /api/delivery/tracking/{id}/mark_picked_up/` - Mark as picked up
- `POST /api/delivery/tracking/{id}/mark_delivered/` - Mark as delivered
- `POST /api/delivery/tracking/{id}/submit_feedback/` - Submit customer feedback
- `GET /api/delivery/tracking/{id}/route_history/` - Get route history
- `GET /api/delivery/tracking/{id}/status_history/` - Get status change history

## Usage

### Creating a Delivery Tracking

```typescript
import { deliveryApi } from '../services/api';

const createTracking = async (orderId: number) => {
  const data = {
    order_id: orderId,
    driver_id: 1, // Optional
    pickup_latitude: 40.7128,
    pickup_longitude: -74.0060,
    delivery_latitude: 40.7589,
    delivery_longitude: -73.9851,
    estimated_delivery_time: '2026-02-06T15:00:00Z',
  };
  
  const tracking = await deliveryApi.createDeliveryTracking(data);
  return tracking;
};
```

### Using the Delivery Map Component

```typescript
import { DeliveryMap } from '../components/delivery';

function MyComponent() {
  return (
    <DeliveryMap 
      tracking={trackingData}
      autoCenter={true}
      height="500px"
      showRoute={true}
    />
  );
}
```

### Using the Delivery Tracker

```typescript
import { DeliveryTracker } from '../components/delivery';

function TrackOrderPage({ orderId }: { orderId: number }) {
  return (
    <DeliveryTracker 
      orderId={orderId}
      refreshInterval={30000} // 30 seconds
    />
  );
}
```

### Using the Delivery Dashboard

```typescript
import { DeliveryDashboard } from '../components/delivery';

function StaffDashboard() {
  return <DeliveryDashboard />;
}
```

## Database Models

### DeliveryPersonnel
- User information and vehicle details
- Current location tracking
- Performance metrics (total deliveries, rating)
- Status (available, on_delivery, off_duty)

### DeliveryTracking
- Order reference
- Driver assignment
- Pickup and delivery coordinates
- Current location
- Time tracking (assigned, picked up, delivered)
- Proof of delivery (photo, signature)
- Customer feedback

### DeliveryRoute
- Route point history
- Coordinates and speed
- Timestamp for each point

### DeliveryStatusHistory
- Status change log
- Changed by (user)
- Notes and timestamps

## Delivery Status Flow

1. **Assigned** - Delivery created and assigned to driver
2. **Picked Up** - Driver picks up the order
3. **In Transit** - Driver is en route to destination
4. **Nearby** - Driver is close to delivery location
5. **Delivered** - Order successfully delivered
6. **Failed** - Delivery attempt failed
7. **Cancelled** - Delivery cancelled

## Location Update Flow

1. Driver app sends location updates every 30 seconds
2. Location stored in `DeliveryTracking.current_latitude/longitude`
3. Route point recorded in `DeliveryRoute` table
4. Driver's location updated in `DeliveryPersonnel`
5. Customer sees real-time location on map

## Customer Feedback System

After delivery is marked as complete:
1. Customer receives option to rate delivery
2. Rating (1-5 stars) and optional comment
3. Feedback stored in `DeliveryTracking`
4. Driver's average rating automatically updated
5. Feedback visible to staff in driver management

## Performance Optimization

### Backend
- Use `select_related` and `prefetch_related` for queries
- Index on frequently queried fields (status, driver, order)
- Pagination for list endpoints

### Frontend
- Auto-refresh with configurable intervals
- Lazy loading for map tiles
- Memoized components for performance
- Optimistic updates for better UX

## Testing

### Backend Tests
```bash
cd backend
python manage.py test delivery
```

### Frontend Tests
```bash
cd DesiDeliver-frontend
npm test
```

## Next Steps

1. **Add WebSocket support** for real-time updates instead of polling
2. **Push notifications** for delivery status changes
3. **Route optimization** algorithm for multiple deliveries
4. **Analytics dashboard** for delivery performance
5. **Mobile driver app** for Android/iOS
6. **Geofencing** for automatic status updates
7. **SMS notifications** for customers

## Troubleshooting

### Map not displaying
- Ensure Leaflet CSS is imported in `index.tsx`
- Check that coordinates are valid numbers
- Verify network access to OpenStreetMap tiles

### Location updates not working
- Check backend CORS settings
- Verify authentication tokens
- Ensure location permissions in browser

### API errors
- Check backend server is running
- Verify database migrations are complete
- Check API_BASE_URL in frontend config

## Support

For issues or questions:
1. Check the GitHub repository issues
2. Review the API documentation
3. Contact the development team

## License

This feature is part of the DesiDeliver project and follows the same license.
