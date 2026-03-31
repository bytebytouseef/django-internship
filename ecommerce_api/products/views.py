from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter
from drf_spectacular.types import OpenApiTypes

from .models import Category, Product
from .serializers import CategorySerializer, ProductListSerializer, ProductDetailSerializer
from .permissions import IsAdminOrReadOnly, IsOwnerOrReadOnly
from .filters import ProductFilter, InStockFilterBackend
from .pagination import StandardPageNumberPagination, LargeResultsSetPagination


@extend_schema_view(
    list=extend_schema(
        summary='List all categories',
        tags=['Products'],
    ),
    create=extend_schema(
        summary='Create a category (admin only)',
        tags=['Products'],
    ),
)
class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]
    pagination_class = None   # No pagination for categories (small list)


@extend_schema_view(
    list=extend_schema(
        summary='List products with filtering, search, and pagination',
        tags=['Products'],
        parameters=[
            OpenApiParameter('q', OpenApiTypes.STR, description='Search term'),
            OpenApiParameter('min_price', OpenApiTypes.FLOAT, description='Minimum price'),
            OpenApiParameter('max_price', OpenApiTypes.FLOAT, description='Maximum price'),
            OpenApiParameter('category', OpenApiTypes.STR, description='Category slug'),
            OpenApiParameter('in_stock', OpenApiTypes.BOOL, description='In stock only'),
            OpenApiParameter('ordering', OpenApiTypes.STR, description='Field to order by'),
        ]
    ),
    retrieve=extend_schema(summary='Get product details', tags=['Products']),
    create=extend_schema(summary='Create product (admin)', tags=['Products']),
    update=extend_schema(summary='Update product (admin)', tags=['Products']),
    partial_update=extend_schema(summary='Partial update (admin)', tags=['Products']),
    destroy=extend_schema(summary='Delete product (admin)', tags=['Products']),
)
class ProductViewSet(viewsets.ModelViewSet):
    """
    Full CRUD for Products.

    Demonstrates ALL filtering, search, ordering, pagination, throttling.
    """
    queryset = Product.objects.select_related('category', 'created_by').all()
    permission_classes = [IsAdminOrReadOnly]

    # ── THROTTLING (Scoped) ──
    # ScopedRateThrottle reads the throttle_scope attribute
    # Rate defined in DEFAULT_THROTTLE_RATES['products']
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'products'

    # ── FILTERING ──
    # Multiple backends can be stacked — all are applied in order
    filter_backends = [
        InStockFilterBackend,       # Custom backend (filters inactive products)
        DjangoFilterBackend,        # filterset_class for structured filters
        SearchFilter,               # ?search= with prefix lookups
        OrderingFilter,             # ?ordering= for sorting
    ]

    # DjangoFilterBackend — uses ProductFilter for rich filtering
    filterset_class = ProductFilter

    # SearchFilter — search_fields with lookup prefixes:
    # ^ = starts with
    # = = exact match
    # @ = full-text search (MySQL only)
    # $ = regex match
    # (no prefix) = icontains (default)
    search_fields = [
        'name',          # icontains
        '^sku',          # starts with
        '=slug',         # exact
        'description',   # icontains
        'category__name' # related field
    ]

    # OrderingFilter — fields clients can sort by
    ordering_fields = ['price', 'created_at', 'name', 'stock', 'rating']
    ordering = ['-created_at']   # Default ordering

    # ── PAGINATION ──
    # Override global pagination for this viewset
    pagination_class = StandardPageNumberPagination

    def get_serializer_class(self):
        """Different serializers for list vs detail."""
        if self.action == 'list':
            return ProductListSerializer
        return ProductDetailSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        # Admins see all products; others see only active ones
        # (InStockFilterBackend handles this too, but belt-and-suspenders)
        return qs

    # ── CUSTOM @action ──
    @extend_schema(summary='Get featured products', tags=['Products'])
    @action(
        detail=False,          # False = list action (/products/featured/)
        methods=['GET'],
        permission_classes=[AllowAny],
        url_path='featured',   # URL segment
        url_name='featured',   # URL name for reverse()
    )
    def featured(self, request):
        """
        Custom action — adds a non-standard endpoint to the ViewSet.
        @action(detail=False) → /api/v1/products/featured/
        @action(detail=True)  → /api/v1/products/{pk}/similar/
        """
        featured = Product.objects.filter(is_featured=True, is_active=True)[:8]
        serializer = ProductListSerializer(featured, many=True, context={'request': request})
        return Response({'results': serializer.data})

    @extend_schema(summary='Toggle product active status (admin)', tags=['Products'])
    @action(
        detail=True,           # True = detail action (/products/{pk}/toggle-active/)
        methods=['POST'],
        permission_classes=[IsAdminUser],
        url_path='toggle-active',
    )
    def toggle_active(self, request, pk=None):
        """Admin action to toggle a product's active status."""
        product = self.get_object()   # get_object() also calls check_object_permissions()
        product.is_active = not product.is_active
        product.save(update_fields=['is_active'])
        return Response({
            'id': product.id,
            'name': product.name,
            'is_active': product.is_active,
            'message': f'Product {"activated" if product.is_active else "deactivated"}.'
        })

    @extend_schema(summary='Get low stock products (admin)', tags=['Products'])
    @action(
        detail=False,
        methods=['GET'],
        permission_classes=[IsAdminUser],
        url_path='low-stock',
    )
    def low_stock(self, request):
        """Returns products with stock below threshold."""
        threshold = int(request.query_params.get('threshold', 10))
        products = Product.objects.filter(stock__lte=threshold, is_active=True).order_by('stock')
        serializer = ProductListSerializer(products, many=True, context={'request': request})
        return Response({
            'threshold': threshold,
            'count': products.count(),
            'results': serializer.data
        })