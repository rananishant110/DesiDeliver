from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db import transaction
from .models import Cart, CartItem
from .serializers import (
    CartSerializer, CartItemSerializer, 
    AddToCartSerializer, UpdateCartItemSerializer
)
from products.models import Product


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_cart(request):
    """Get user's current cart with all items"""
    try:
        cart, created = Cart.objects.get_or_create(
            user=request.user,
            is_active=True,
            defaults={'user': request.user}
        )
        
        serializer = CartSerializer(cart)
        return Response(serializer.data)
    except Exception as e:
        return Response(
            {'error': 'Failed to retrieve cart'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_to_cart(request):
    """Add a product to the user's cart"""
    serializer = AddToCartSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        with transaction.atomic():
            # Get or create user's cart
            cart, created = Cart.objects.get_or_create(
                user=request.user,
                is_active=True,
                defaults={'user': request.user}
            )
            
            product_id = serializer.validated_data['product_id']
            quantity = serializer.validated_data['quantity']
            
            # Check if product exists and is active
            product = get_object_or_404(Product, id=product_id, is_active=True)
            
            # Check if product is already in cart
            cart_item, created = CartItem.objects.get_or_create(
                cart=cart,
                product=product,
                defaults={'quantity': quantity}
            )
            
            if not created:
                # Update quantity if item already exists
                cart_item.quantity += quantity
                cart_item.save()
            
            # Refresh cart to get updated totals
            cart.refresh_from_db()
            
            # Return updated cart
            cart_serializer = CartSerializer(cart)
            return Response(cart_serializer.data, status=status.HTTP_200_OK)
            
    except Product.DoesNotExist:
        return Response(
            {'error': 'Product not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {'error': 'Failed to add item to cart'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def update_cart_item(request, item_id):
    """Update quantity of a cart item"""
    serializer = UpdateCartItemSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # Get cart item and verify ownership
        cart_item = get_object_or_404(
            CartItem, 
            id=item_id, 
            cart__user=request.user,
            cart__is_active=True
        )
        
        quantity = serializer.validated_data['quantity']
        cart_item.quantity = quantity
        cart_item.save()
        
        # Return updated cart
        cart = cart_item.cart
        cart.refresh_from_db()
        cart_serializer = CartSerializer(cart)
        return Response(cart_serializer.data)
        
    except CartItem.DoesNotExist:
        return Response(
            {'error': 'Cart item not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {'error': 'Failed to update cart item'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def remove_from_cart(request, item_id):
    """Remove an item from the user's cart"""
    try:
        # Get cart item and verify ownership
        cart_item = get_object_or_404(
            CartItem, 
            id=item_id, 
            cart__user=request.user,
            cart__is_active=True
        )
        
        cart = cart_item.cart
        cart_item.delete()
        
        # Return updated cart
        cart.refresh_from_db()
        cart_serializer = CartSerializer(cart)
        return Response(cart_serializer.data)
        
    except CartItem.DoesNotExist:
        return Response(
            {'error': 'Cart item not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {'error': 'Failed to remove item from cart'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def clear_cart(request):
    """Clear all items from the user's cart"""
    try:
        cart = get_object_or_404(
            Cart, 
            user=request.user, 
            is_active=True
        )
        
        # Remove all cart items
        cart.items.all().delete()
        
        # Return empty cart
        cart.refresh_from_db()
        cart_serializer = CartSerializer(cart)
        return Response(cart_serializer.data)
        
    except Cart.DoesNotExist:
        return Response(
            {'error': 'Cart not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {'error': 'Failed to clear cart'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def cart_summary(request):
    """Get a summary of the user's cart (counts and totals)"""
    try:
        cart = get_object_or_404(
            Cart, 
            user=request.user, 
            is_active=True
        )
        
        summary = {
            'total_items': cart.total_items,
            'total_quantity': float(cart.total_quantity),
            'item_count': cart.items.count()
        }
        
        return Response(summary)
        
    except Cart.DoesNotExist:
        return Response({
            'total_items': 0,
            'total_quantity': 0.0,
            'item_count': 0
        })
    except Exception as e:
        return Response(
            {'error': 'Failed to get cart summary'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
