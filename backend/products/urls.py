from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    # Category endpoints
    path('categories/', views.CategoryListView.as_view(), name='category-list'),
    
    # Product endpoints
    path('', views.ProductListView.as_view(), name='product-list'),
    path('search/', views.ProductSearchView.as_view(), name='product-search'),
    path('<int:pk>/', views.ProductDetailView.as_view(), name='product-detail'),
    
    # Utility endpoints
    path('stats/', views.product_stats_view, name='product-stats'),
    path('featured/', views.featured_products_view, name='featured-products'),
]
