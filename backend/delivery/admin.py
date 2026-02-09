from django.contrib import admin
from .models import DeliveryPersonnel, DeliveryTracking, DeliveryRoute, DeliveryStatusHistory


@admin.register(DeliveryPersonnel)
class DeliveryPersonnelAdmin(admin.ModelAdmin):
    list_display = ['employee_id', 'user', 'vehicle_type', 'status', 'total_deliveries', 'average_rating']
    list_filter = ['status', 'vehicle_type']
    search_fields = ['employee_id', 'user__username', 'user__first_name', 'user__last_name']
    readonly_fields = ['created_at', 'updated_at', 'last_location_update']
    
    fieldsets = (
        ('Personal Information', {
            'fields': ('user', 'employee_id', 'phone_number')
        }),
        ('Vehicle Information', {
            'fields': ('vehicle_type', 'vehicle_number', 'license_number')
        }),
        ('Status', {
            'fields': ('status',)
        }),
        ('Current Location', {
            'fields': ('current_latitude', 'current_longitude', 'last_location_update')
        }),
        ('Performance Metrics', {
            'fields': ('total_deliveries', 'successful_deliveries', 'average_rating')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(DeliveryTracking)
class DeliveryTrackingAdmin(admin.ModelAdmin):
    list_display = ['order', 'driver', 'status', 'assigned_at', 'delivered_at']
    list_filter = ['status', 'assigned_at', 'delivered_at']
    search_fields = ['order__order_number', 'driver__employee_id', 'driver__user__username']
    readonly_fields = ['assigned_at', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Order & Driver', {
            'fields': ('order', 'driver')
        }),
        ('Status', {
            'fields': ('status',)
        }),
        ('Pickup Location', {
            'fields': ('pickup_latitude', 'pickup_longitude')
        }),
        ('Delivery Location', {
            'fields': ('delivery_latitude', 'delivery_longitude')
        }),
        ('Current Location', {
            'fields': ('current_latitude', 'current_longitude')
        }),
        ('Time Tracking', {
            'fields': ('assigned_at', 'picked_up_at', 'delivered_at', 'estimated_delivery_time')
        }),
        ('Distance', {
            'fields': ('total_distance',)
        }),
        ('Delivery Proof', {
            'fields': ('delivery_notes', 'proof_of_delivery_photo', 'customer_signature')
        }),
        ('Customer Feedback', {
            'fields': ('customer_rating', 'customer_feedback')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(DeliveryRoute)
class DeliveryRouteAdmin(admin.ModelAdmin):
    list_display = ['tracking', 'latitude', 'longitude', 'speed', 'recorded_at']
    list_filter = ['recorded_at']
    search_fields = ['tracking__order__order_number']
    readonly_fields = ['recorded_at']


@admin.register(DeliveryStatusHistory)
class DeliveryStatusHistoryAdmin(admin.ModelAdmin):
    list_display = ['tracking', 'status', 'changed_by', 'timestamp']
    list_filter = ['status', 'timestamp']
    search_fields = ['tracking__order__order_number']
    readonly_fields = ['timestamp']
