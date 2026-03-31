from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field
from .models import Category, Product


class CategorySerializer(serializers.ModelSerializer):
    product_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description', 'product_count']
        read_only_fields = ['id']

    @extend_schema_field(serializers.IntegerField())
    def get_product_count(self, obj):
        return obj.products.filter(is_active=True).count()


class ProductListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for list views."""
    category_name = serializers.CharField(source='category.name', read_only=True)
    is_in_stock = serializers.BooleanField(read_only=True)
    discount_percentage = serializers.FloatField(read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'price', 'compare_price',
            'discount_percentage', 'category_name', 'stock',
            'is_in_stock', 'condition', 'is_featured', 'image',
        ]


class ProductDetailSerializer(serializers.ModelSerializer):
    """Full serializer for create/update/retrieve."""
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        source='category',
        write_only=True
    )
    is_in_stock = serializers.SerializerMethodField()
    discount_percentage = serializers.SerializerMethodField()
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'description', 'price', 'compare_price',
            'discount_percentage', 'stock', 'is_in_stock', 'sku',
            'category', 'category_id', 'condition', 'is_active',
            'is_featured', 'image', 'created_by_username',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'created_by_username']

    @extend_schema_field(serializers.BooleanField())
    def get_is_in_stock(self, obj):
        return obj.stock > 0

    @extend_schema_field(serializers.FloatField())
    def get_discount_percentage(self, obj):
        return obj.discount_percentage

    def validate_price(self, value):
        if value < 0:
            raise serializers.ValidationError('Price cannot be negative.')
        return value

    def validate_sku(self, value):
        return value.upper().strip()

    def validate(self, data):
        """Cross-field: compare_price must be greater than price."""
        price = data.get('price', getattr(self.instance, 'price', None))
        compare_price = data.get('compare_price')
        if compare_price and price and compare_price <= price:
            raise serializers.ValidationError({
                'compare_price': 'Compare price must be greater than the sale price.'
            })
        return data

    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)