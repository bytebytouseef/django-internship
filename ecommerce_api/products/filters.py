from django_filters import rest_framework as filters
from rest_framework.filters import BaseFilterBackend
from .models import Product, Category


class ProductFilter(filters.FilterSet):
    """
    DjangoFilterBackend filterset — declarative filtering.

    filterset_fields on the view is a shortcut for simple equality filters.
    FilterSet gives you full control: range filters, custom lookups, etc.
    """
    # Exact match filters
    category = filters.CharFilter(field_name='category__slug', lookup_expr='exact')
    condition = filters.ChoiceFilter(choices=Product.CONDITION_CHOICES)
    is_featured = filters.BooleanFilter()
    in_stock = filters.BooleanFilter(method='filter_in_stock', label='In Stock Only')

    # Range filters
    min_price = filters.NumberFilter(field_name='price', lookup_expr='gte')
    max_price = filters.NumberFilter(field_name='price', lookup_expr='lte')
    min_stock = filters.NumberFilter(field_name='stock', lookup_expr='gte')

    # Date filters
    created_after = filters.DateFilter(field_name='created_at', lookup_expr='date__gte')
    created_before = filters.DateFilter(field_name='created_at', lookup_expr='date__lte')

    class Meta:
        model = Product
        fields = [
            'category', 'condition', 'is_featured',
            'in_stock', 'min_price', 'max_price',
        ]

    def filter_in_stock(self, queryset, name, value):
        """Custom filter method — called when in_stock param is present."""
        if value:
            return queryset.filter(stock__gt=0)
        return queryset.filter(stock=0)


class InStockFilterBackend(BaseFilterBackend):
    """
    Custom FilterBackend — applies a default filter regardless of query params.
    This one ensures only active products are shown by default.

    Writing a custom FilterBackend:
    1. Extend BaseFilterBackend
    2. Implement filter_queryset(request, queryset, view)
    3. Add to view's filter_backends list
    """

    def filter_queryset(self, request, queryset, view):
        """
        Called automatically by DRF for every request.
        Can read request.query_params to apply conditional logic.
        """
        # Show inactive products only to admin users
        if not request.user.is_staff:
            queryset = queryset.filter(is_active=True)
        return queryset

    def get_schema_operation_parameters(self, view):
        """Describe this filter for OpenAPI schema generation."""
        return [
            {
                'name': 'active_only',
                'required': False,
                'in': 'query',
                'description': 'Filter to show only active products (non-admin users always see active only)',
                'schema': {'type': 'boolean'},
            }
        ]