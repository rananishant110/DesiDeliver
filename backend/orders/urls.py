from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    # Order creation and management
    path('create/', views.create_order, name='create_order'),
    path('list/', views.get_orders, name='get_orders'),
    path('<int:order_id>/', views.get_order, name='get_order'),
    path('<int:order_id>/cancel/', views.cancel_order, name='cancel_order'),
    
    # Order status management (admin/staff only)
    path('<int:order_id>/status/', views.update_order_status, name='update_order_status'),
    
    # Order statistics
    path('stats/', views.order_stats, name='order_stats'),
    
    # CSV download endpoints
    path('<int:order_id>/csv/', views.download_order_csv, name='download_order_csv'),
    path('summary/csv/', views.download_orders_summary_csv, name='download_orders_summary_csv'),
    path('daily/csv/', views.download_daily_orders_csv, name='download_daily_orders_csv'),
    path('daily/email/', views.send_daily_summary_email, name='send_daily_summary_email'),
    path('bulk-process/', views.bulk_process_orders, name='bulk_process_orders'),
    path('staff/', views.get_orders_for_staff, name='get_orders_for_staff'),
    
    # Catalog-based CSV generation
    path('catalog/generate-csv/', views.generate_order_csv_from_text, name='generate_order_csv_from_text'),
    path('catalog/stats/', views.get_catalog_stats, name='get_catalog_stats'),
]
