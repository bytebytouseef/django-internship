from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.throttling import ScopedRateThrottle
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiResponse

from .models import Order
from .serializers import OrderSerializer, OrderCreateSerializer
from .permissions import IsOrderOwner
from products.pagination import SmallResultsSetPagination


@extend_schema_view(
    list=extend_schema(summary='List my orders', tags=['Orders']),
    retrieve=extend_schema(summary='Get order details', tags=['Orders']),
    create=extend_schema(summary='Place a new order', tags=['Orders']),
    destroy=extend_schema(summary='Delete order (admin only)', tags=['Orders']),
)
class OrderViewSet(viewsets.ModelViewSet):
    """
    Orders ViewSet — demonstrates:
    - Object-level permissions (IsOrderOwner)
    - Custom @action (cancel, reorder)
    - Filtered queryset per user
    - ScopedRateThrottle
    """
    serializer_class = OrderSerializer
    permission_classes = [IsOrderOwner]

    # Scoped throttle — rate defined in DEFAULT_THROTTLE_RATES['orders']
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'orders'

    pagination_class = SmallResultsSetPagination

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status', 'payment_status']
    search_fields = ['items__product_name', 'shipping_city']
    ordering_fields = ['created_at', 'total', 'status']
    ordering = ['-created_at']

    # No update or partial_update — orders use dedicated actions
    http_method_names = ['get', 'post', 'delete', 'head', 'options']

    def get_queryset(self):
        """
        Object-level security starts HERE:
        - Regular users only see THEIR orders
        - Admins see ALL orders

        This is the first layer of protection.
        has_object_permission() is the second layer (per-object).
        """
        user = self.request.user
        if user.is_staff:
            return Order.objects.select_related('user').prefetch_related(
                'items', 'items__product'
            ).all()
        # Non-admin users: filter to own orders only
        return Order.objects.select_related('user').prefetch_related(
            'items', 'items__product'
        ).filter(user=user)

    def get_serializer_class(self):
        if self.action == 'create':
            return OrderCreateSerializer
        return OrderSerializer

    def create(self, request, *args, **kwargs):
        """Create order and return full order details."""
        serializer = OrderCreateSerializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        order = serializer.save()

        # Return the full order using read serializer
        response_serializer = OrderSerializer(order, context={'request': request})
        return Response(
            {'message': 'Order placed successfully!', 'order': response_serializer.data},
            status=status.HTTP_201_CREATED
        )

    def destroy(self, request, *args, **kwargs):
        """Only admins can delete orders."""
        if not request.user.is_staff:
            return Response(
                {'error': 'Only administrators can delete orders.'},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().destroy(request, *args, **kwargs)

    # ── CUSTOM @action: CANCEL ──
    @extend_schema(
        summary='Cancel an order',
        tags=['Orders'],
        responses={
            200: OpenApiResponse(description='Order cancelled successfully'),
            400: OpenApiResponse(description='Order cannot be cancelled'),
        }
    )
    @action(
        detail=True,           # /orders/{pk}/cancel/
        methods=['POST'],
        url_path='cancel',
        url_name='cancel',
    )
    def cancel(self, request, pk=None):
        """
        Cancel an order.
        Only the order owner can cancel, and only if status allows it.

        get_object() automatically calls check_object_permissions()
        which invokes IsOrderOwner.has_object_permission().
        """
        order = self.get_object()  # ← triggers has_object_permission()

        if not order.can_cancel:
            return Response(
                {
                    'error': f'Order cannot be cancelled. Current status: {order.get_status_display()}',
                    'cancellable_statuses': ['pending', 'confirmed'],
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # Restore stock for each item
        for item in order.items.select_related('product').all():
            item.product.stock += item.quantity
            item.product.save(update_fields=['stock'])

        order.status = 'cancelled'
        order.save(update_fields=['status', 'updated_at'])

        serializer = self.get_serializer(order)
        return Response({
            'message': f'Order #{order.pk} has been cancelled.',
            'order': serializer.data
        })

    # ── CUSTOM @action: REORDER ──
    @extend_schema(summary='Reorder — place a new order with same items', tags=['Orders'])
    @action(detail=True, methods=['POST'], url_path='reorder')
    def reorder(self, request, pk=None):
        """Creates a new order with the same items as an existing one."""
        original_order = self.get_object()

        # Build items data from original order
        items_data = []
        unavailable = []
        for item in original_order.items.select_related('product').all():
            if item.product.is_active and item.product.stock >= item.quantity:
                items_data.append({
                    'product_id': item.product.id,
                    'quantity': item.quantity,
                })
            else:
                unavailable.append(item.product_name)

        if not items_data:
            return Response(
                {'error': 'No items are available for reorder.', 'unavailable': unavailable},
                status=status.HTTP_400_BAD_REQUEST
            )

        new_order_data = {
            'shipping_address': original_order.shipping_address,
            'shipping_city': original_order.shipping_city,
            'shipping_country': original_order.shipping_country,
            'shipping_zip': original_order.shipping_zip,
            'items': items_data,
        }

        serializer = OrderCreateSerializer(data=new_order_data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        new_order = serializer.save()

        response_serializer = OrderSerializer(new_order, context={'request': request})
        return Response({
            'message': f'New order #{new_order.pk} created from Order #{original_order.pk}.',
            'unavailable_items': unavailable,
            'order': response_serializer.data,
        }, status=status.HTTP_201_CREATED)

    # ── CUSTOM @action: STATS (admin only) ──
    @extend_schema(summary='Order statistics (admin)', tags=['Orders'])
    @action(detail=False, methods=['GET'], url_path='stats')
    def stats(self, request):
        """Aggregate order stats — admin only."""
        if not request.user.is_staff:
            return Response({'error': 'Admin access required.'}, status=status.HTTP_403_FORBIDDEN)

        from django.db.models import Sum, Count, Avg
        stats = Order.objects.aggregate(
            total_orders=Count('id'),
            total_revenue=Sum('total'),
            avg_order_value=Avg('total'),
        )
        by_status = Order.objects.values('status').annotate(count=Count('id'))
        return Response({**stats, 'by_status': list(by_status)})