#!/bin/bash

# Delivery Tracking Setup Script for DesiDeliver
# This script sets up the delivery tracking feature

echo "=========================================="
echo "DesiDeliver - Delivery Tracking Setup"
echo "=========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if we're in the correct directory
if [ ! -d "backend" ] || [ ! -d "DesiDeliver-frontend" ]; then
    echo -e "${RED}Error: Please run this script from the DesiDeliver root directory${NC}"
    exit 1
fi

echo -e "${YELLOW}Step 1: Setting up Backend${NC}"
echo "----------------------------------------"
cd backend

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
elif [ -d "../venv" ]; then
    echo "Activating virtual environment..."
    source ../venv/bin/activate
else
    echo -e "${YELLOW}Warning: No virtual environment found. Please activate it manually if needed.${NC}"
fi

# Run migrations
echo "Creating migrations for delivery app..."
python manage.py makemigrations delivery

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Migrations created successfully${NC}"
else
    echo -e "${RED}✗ Failed to create migrations${NC}"
    exit 1
fi

echo ""
echo "Applying migrations..."
python manage.py migrate

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Migrations applied successfully${NC}"
else
    echo -e "${RED}✗ Failed to apply migrations${NC}"
    exit 1
fi

# Go back to root
cd ..

echo ""
echo -e "${YELLOW}Step 2: Setting up Frontend${NC}"
echo "----------------------------------------"
cd DesiDeliver-frontend

# Install npm packages
echo "Installing npm packages..."
npm install

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ npm packages installed successfully${NC}"
else
    echo -e "${RED}✗ Failed to install npm packages${NC}"
    exit 1
fi

# Go back to root
cd ..

echo ""
echo "=========================================="
echo -e "${GREEN}Setup completed successfully!${NC}"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Start the backend server:"
echo "   cd backend && python manage.py runserver"
echo ""
echo "2. In a new terminal, start the frontend:"
echo "   cd DesiDeliver-frontend && npm start"
echo ""
echo "3. Access the admin panel to add delivery personnel:"
echo "   http://localhost:8000/admin/delivery/"
echo ""
echo "4. View the delivery tracking in the frontend:"
echo "   http://localhost:3000/delivery/dashboard"
echo ""
echo "For more information, see:"
echo "docs/feat-delivery-tracking/README.md"
echo ""
