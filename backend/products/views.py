from rest_framework import generics, status, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from .models import Category, Product
from .serializers import (
    CategorySerializer, ProductListSerializer, 
    ProductDetailSerializer, ProductSearchSerializer
)


class CategoryListView(generics.ListAPIView):
    """List all active categories"""
    
    queryset = Category.objects.filter(is_active=True)
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]
    filterset_fields = ['is_active']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']


class ProductListView(generics.ListAPIView):
    """List products with search, filtering, and pagination"""
    
    serializer_class = ProductListSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'in_stock', 'brand', 'origin', 'is_active']
    search_fields = ['name', 'description', 'item_code', 'brand']
    ordering_fields = ['name', 'item_code', 'created_at', 'stock_quantity']
    ordering = ['name']
    
    def get_queryset(self):
        queryset = Product.objects.filter(is_active=True).select_related('category')
        
        # Custom filtering
        search = self.request.query_params.get('search', '')
        category = self.request.query_params.get('category')
        in_stock = self.request.query_params.get('in_stock')
        brand = self.request.query_params.get('brand')
        origin = self.request.query_params.get('origin')
        
        if search:
            # Enhanced search with multiple strategies
            search_terms = search.strip().split()
            search_filters = Q()
            
            for term in search_terms:
                if term:  # Skip empty terms
                    # Create a filter for each search term
                    term_filter = (
                        Q(name__icontains=term) |
                        Q(description__icontains=term) |
                        Q(item_code__icontains=term) |
                        Q(brand__icontains=term) |
                        Q(origin__icontains=term) |
                        Q(category__name__icontains=term) |
                        Q(category__description__icontains=term)
                    )
                    
                    # Add to main search filter (AND logic between terms)
                    search_filters &= term_filter
            
            # Apply the search filter
            queryset = queryset.filter(search_filters)
        
        if category:
            queryset = queryset.filter(category_id=category)
        
        if in_stock is not None:
            if in_stock.lower() == 'true':
                queryset = queryset.filter(in_stock=True)
            elif in_stock.lower() == 'false':
                queryset = queryset.filter(in_stock=False)
        
        if brand:
            queryset = queryset.filter(brand__icontains=brand)
        
        if origin:
            queryset = queryset.filter(origin__icontains=origin)
        
        return queryset


class ProductDetailView(generics.RetrieveAPIView):
    """Get detailed product information"""
    
    queryset = Product.objects.filter(is_active=True).select_related('category')
    serializer_class = ProductDetailSerializer
    permission_classes = [AllowAny]
    lookup_field = 'pk'


class ProductSearchView(generics.ListAPIView):
    """Advanced product search with custom parameters"""
    
    serializer_class = ProductListSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        serializer = ProductSearchSerializer(data=self.request.query_params)
        serializer.is_valid(raise_exception=True)
        
        queryset = Product.objects.filter(is_active=True).select_related('category')
        
        # Apply search filters
        search = serializer.validated_data.get('search', '')
        category = serializer.validated_data.get('category')
        in_stock = serializer.validated_data.get('in_stock')
        brand = serializer.validated_data.get('brand')
        origin = serializer.validated_data.get('origin')
        
        if search:
            # Enhanced search with multiple strategies
            search_terms = search.strip().split()
            search_filters = Q()
            
            for term in search_terms:
                if term:  # Skip empty terms
                    # Create a filter for each search term
                    term_filter = (
                        Q(name__icontains=term) |
                        Q(description__icontains=term) |
                        Q(item_code__icontains=term) |
                        Q(brand__icontains=term) |
                        Q(origin__icontains=term) |
                        Q(category__name__icontains=term) |
                        Q(category__description__icontains=term)
                    )
                    
                    # Add to main search filter (AND logic between terms)
                    search_filters &= term_filter
            
            # Apply the search filter
            queryset = queryset.filter(search_filters)
        
        if category:
            queryset = queryset.filter(category_id=category)
        
        if in_stock is not None:
            queryset = queryset.filter(in_stock=in_stock)
        
        if brand:
            queryset = queryset.filter(brand__icontains=brand)
        
        if origin:
            queryset = queryset.filter(origin__icontains=origin)
        
        return queryset.order_by('name')


@api_view(['GET'])
@permission_classes([AllowAny])
def product_stats_view(request):
    """Get product catalog statistics"""
    
    total_products = Product.objects.filter(is_active=True).count()
    total_categories = Category.objects.filter(is_active=True).count()
    in_stock_products = Product.objects.filter(is_active=True, in_stock=True).count()
    low_stock_products = Product.objects.filter(
        is_active=True, 
        stock_quantity__lte=10
    ).count()
    
    # Category breakdown
    category_stats = []
    categories = Category.objects.filter(is_active=True)
    for category in categories:
        product_count = Product.objects.filter(
            category=category, 
            is_active=True
        ).count()
        if product_count > 0:
            category_stats.append({
                'category': category.name,
                'product_count': product_count
            })
    
    return Response({
        'total_products': total_products,
        'total_categories': total_categories,
        'in_stock_products': in_stock_products,
        'low_stock_products': low_stock_products,
        'category_breakdown': category_stats
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def featured_products_view(request):
    """Get featured products (recently added, in stock)"""
    
    featured_products = Product.objects.filter(
        is_active=True,
        in_stock=True
    ).order_by('-created_at')[:8]
    
    serializer = ProductListSerializer(featured_products, many=True)
    return Response(serializer.data)
