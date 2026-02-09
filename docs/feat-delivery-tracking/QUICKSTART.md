# Quick Start Guide - Delivery Tracking Feature

## Prerequisites
- Python 3.8+ with Django installed
- Node.js 16+ with npm
- PostgreSQL or SQLite database
- DesiDeliver backend and frontend setup

## Quick Setup (5 minutes)

### Option 1: Automated Setup
Run the provided setup script:
```bash
cd /Users/neelam/Desktop/apps/DesiDeliver
./setup_delivery_tracking.sh
```

### Option 2: Manual Setup

#### Backend Setup
```bash
cd backend

# Create and apply migrations
python manage.py makemigrations delivery
python manage.py migrate

# Verify the installation
python manage.py showmigrations delivery
```

#### Frontend Setup
```bash
cd DesiDeliver-frontend

# Install dependencies
npm install
```

## Testing the Feature

### 1. Start the Backend Server
```bash
cd backend
python manage.py runserver
```

### 2. Start the Frontend Server
```bash
cd DesiDeliver-frontend
npm start
```

### 3. Create Test Data

#### Option A: Using Django Admin
1. Go to http://localhost:8000/admin/
2. Navigate to "Delivery Management" section
3. Add Delivery Personnel:
   - Select a user (must be created first)
   - Enter employee ID, phone, vehicle details
   - Save

#### Option B: Using Django Shell
```bash
python manage.py shell
```

```python
from users.models import User
from delivery.models import DeliveryPersonnel, DeliveryTracking
from orders.models import Order

# Create a delivery driver user
driver_user = User.objects.create_user(
    username='driver1',
    email='driver1@example.com',
    password='password123',
    first_name='John',
    last_name='Driver',
    phone_number='555-0123'
)

# Create delivery personnel profile
driver = DeliveryPersonnel.objects.create(
    user=driver_user,
    employee_id='DRV001',
    phone_number='555-0123',
    vehicle_type='van',
    vehicle_number='ABC-1234',
    license_number='DL12345678',
    status='available'
)

# Get an existing order
order = Order.objects.first()

# Create delivery tracking
tracking = DeliveryTracking.objects.create(
    order=order,
    driver=driver,
    status='assigned',
    pickup_latitude=40.7128,
    pickup_longitude=-74.0060,
    delivery_latitude=40.7589,
    delivery_longitude=-73.9851,
    current_latitude=40.7128,
    current_longitude=-74.0060
)

print(f"Created tracking: {tracking.id}")
```

### 4. Access the Features

#### Customer View
- Track Order: http://localhost:3000/delivery/track/{order_id}
- View delivery map and real-time status

#### Staff View
- Delivery Dashboard: http://localhost:3000/delivery/dashboard
- Driver Management: http://localhost:3000/delivery/management
- View all active deliveries

## API Testing

### Using curl

```bash
# Get all delivery personnel
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/api/delivery/personnel/

# Get delivery tracking for an order
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/api/delivery/tracking/?order=1

# Update driver location
curl -X PATCH \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"latitude": 40.7589, "longitude": -73.9851, "speed": 45.5}' \
  http://localhost:8000/api/delivery/tracking/1/update_location/

# Mark delivery as picked up
curl -X POST \
  -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/api/delivery/tracking/1/mark_picked_up/
```

### Using Python requests

```python
import requests

base_url = "http://localhost:8000/api"
token = "YOUR_ACCESS_TOKEN"
headers = {"Authorization": f"Bearer {token}"}

# Create delivery tracking
data = {
    "order_id": 1,
    "driver_id": 1,
    "pickup_latitude": 40.7128,
    "pickup_longitude": -74.0060,
    "delivery_latitude": 40.7589,
    "delivery_longitude": -73.9851
}
response = requests.post(f"{base_url}/delivery/tracking/", json=data, headers=headers)
tracking = response.json()

# Update location
location_data = {
    "latitude": 40.7400,
    "longitude": -74.0000,
    "speed": 35.0
}
response = requests.patch(
    f"{base_url}/delivery/tracking/{tracking['id']}/update_location/",
    json=location_data,
    headers=headers
)
```

## Common Issues & Solutions

### Issue: Map not displaying
**Solution**: 
- Clear browser cache
- Check console for JavaScript errors
- Verify Leaflet CSS is loaded
- Check coordinates are valid numbers

### Issue: "No tracking found for this order"
**Solution**:
- Create a DeliveryTracking record for the order
- Ensure the order exists and is in 'ready' or later status

### Issue: Location updates not working
**Solution**:
- Check CORS settings in Django
- Verify authentication token is valid
- Ensure coordinates are in correct format (decimal degrees)

### Issue: Migration errors
**Solution**:
```bash
# Reset migrations (use with caution in production)
python manage.py migrate delivery zero
python manage.py makemigrations delivery
python manage.py migrate delivery
```

## Next Steps

1. **Customize the map**: Edit `DeliveryMap.tsx` to add custom markers or styling
2. **Add notifications**: Implement WebSocket or push notifications for real-time updates
3. **Mobile app**: Create a companion mobile app for drivers
4. **Analytics**: Add delivery performance metrics and reporting
5. **Route optimization**: Implement multi-stop route planning

## Support

For detailed documentation, see:
- `/docs/feat-delivery-tracking/README.md`
- GitHub Copilot instructions: `/.github/copilot-instructions.md`

## Verification Checklist

- [ ] Backend migrations applied successfully
- [ ] Frontend dependencies installed
- [ ] At least one delivery personnel created
- [ ] Delivery tracking record created
- [ ] Map displays correctly in browser
- [ ] API endpoints responding correctly
- [ ] Real-time updates working (30-second refresh)
- [ ] Customer can submit feedback
- [ ] Staff can view delivery dashboard

If all items are checked, your delivery tracking system is ready to use!
