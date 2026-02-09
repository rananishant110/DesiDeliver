from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DeliveryPersonnelViewSet, DeliveryTrackingViewSet

router = DefaultRouter()
router.register(r'personnel', DeliveryPersonnelViewSet, basename='delivery-personnel')
router.register(r'tracking', DeliveryTrackingViewSet, basename='delivery-tracking')

urlpatterns = [
    path('', include(router.urls)),
]
