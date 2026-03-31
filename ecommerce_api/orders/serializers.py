from rest_framework import serializers
from .models import Order, OrderItem
from products.models import Product
from products.serializers import ProductListSerializer


class OrderItemSerializer(serializers.ModelSerializer):
    product_detail = ProductListSerializer(source='product', read_only=True)
    line_total = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = OrderItem
        fields = [
            'id', 'product', 'product_detail',
            'product_name', 'product_sku',
            'unit_price', 'quantity', 'line_total',
        ]
        read_only_fields = ['product_name', 'product_sku', 'unit_price']


class OrderItemCreateSerializer(serializers.Serializer):
    """Used only during order creation — simpler input."""
    product_id = serializers.PrimaryKeyRelatedField(queryset=Product.objects.filter(is_active=True))
    quantity = serializers.IntegerField(min_value=1, max_value=100)

    def validate(self, data):
        product = data['product_id']
        quantity = data['quantity']
        if product.stock < quantity:
            raise serializers.ValidationError(
                f'Insufficient stock. Available: {product.stock}, Requested: {quantity}'
            )
        return data


class OrderCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating orders."""
    items = OrderItemCreateSerializer(many=True, write_only=True)

    class Meta:
        model = Order
        fields = [
            'shipping_address', 'shipping_city',
            'shipping_country', 'shipping_zip',
            'notes', 'items',
        ]

    def validate_items(self, value):
        if not value:
            raise serializers.ValidationError('Order must have at least one item.')
        # Check for duplicate products
        product_ids = [item['product_id'].id for item in value]
        if len(product_ids) != len(set(product_ids)):
            raise serializers.ValidationError('Duplicate products in order.')
        return value

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        user = self.context['request'].user

        order = Order.objects.create(user=user, **validated_data)

        for item_data in items_data:
            product = item_data['product_id']
            quantity = item_data['quantity']
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=quantity,
            )
            # Deduct stock
            product.stock -= quantity
            product.save(update_fields=['stock'])

        order.calculate_totals()
        return order


class OrderSerializer(serializers.ModelSerializer):
    """Full order serializer for reading."""
    items = OrderItemSerializer(many=True, read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    payment_status_display = serializers.CharField(source='get_payment_status_display', read_only=True)
    can_cancel = serializers.BooleanField(read_only=True)
    item_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'username', 'status', 'status_display',
            'payment_status', 'payment_status_display',
            'shipping_address', 'shipping_city', 'shipping_country', 'shipping_zip',
            'subtotal', 'shipping_cost', 'total',
            'notes', 'can_cancel', 'item_count', 'items',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'subtotal', 'total', 'created_at', 'updated_at']