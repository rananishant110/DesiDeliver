from django.urls import path
from . import views

app_name = 'cart'

urlpatterns = [
    # Cart management
    path('', views.get_cart, name='get_cart'),
    path('add/', views.add_to_cart, name='add_to_cart'),
    path('clear/', views.clear_cart, name='clear_cart'),
    path('summary/', views.cart_summary, name='cart_summary'),
    
    # Cart item management
    path('items/<int:item_id>/update/', views.update_cart_item, name='update_cart_item'),
    path('items/<int:item_id>/remove/', views.remove_from_cart, name='remove_from_cart'),
]
