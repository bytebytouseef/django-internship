from rest_framework import serializers
from .models import Author, Book


# ============================================================
# AUTHOR SERIALIZERS
# ============================================================

class AuthorSerializer(serializers.ModelSerializer):
    """
    Full Author serializer — used for author CRUD endpoints.

    ModelSerializer automatically generates fields from the model.
    It also auto-generates create() and update() methods.
    Compare to serializers.Serializer which requires manual field
    definitions AND manual create()/update() implementations.
    """

    # SerializerMethodField — computed field, not a model field
    # Calls get_<field_name>(self, obj) automatically
    full_name = serializers.SerializerMethodField()

    # A computed count of books — also a SerializerMethodField
    book_count = serializers.SerializerMethodField()

    class Meta:
        model = Author
        fields = [
            'id', 'first_name', 'last_name', 'full_name',
            'bio', 'birth_date', 'nationality',
            'book_count', 'created_at'
        ]
        # read_only_fields — included in output but never written to
        read_only_fields = ['id', 'created_at']

    def get_full_name(self, obj):
        """obj is the Author instance being serialized."""
        return f'{obj.first_name} {obj.last_name}'

    def get_book_count(self, obj):
        """Count books via the reverse FK relation (related_name='books')."""
        return obj.books.count()

    # ── FIELD-LEVEL VALIDATION ──
    # validate_<fieldname>() is called during .is_valid()
    def validate_first_name(self, value):
        if len(value.strip()) < 2:
            raise serializers.ValidationError(
                'First name must be at least 2 characters.'
            )
        return value.strip().title()   # Normalize to Title Case

    def validate_last_name(self, value):
        if len(value.strip()) < 2:
            raise serializers.ValidationError(
                'Last name must be at least 2 characters.'
            )
        return value.strip().title()

    # ── CROSS-FIELD VALIDATION ──
    # validate() runs after all individual field validators pass
    def validate(self, data):
        first = data.get('first_name', '')
        last = data.get('last_name', '')
        if first and last and first.lower() == last.lower():
            raise serializers.ValidationError(
                'First name and last name cannot be identical.'
            )
        return data


class AuthorMinimalSerializer(serializers.ModelSerializer):
    """
    Lightweight Author serializer — used NESTED inside BookSerializer.
    Only includes fields relevant when viewing a book.
    Avoids circular nesting (no 'books' field here).
    """
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = Author
        fields = ['id', 'full_name', 'nationality']

    def get_full_name(self, obj):
        return f'{obj.first_name} {obj.last_name}'


# ============================================================
# BOOK SERIALIZERS
# ============================================================

class BookSerializer(serializers.ModelSerializer):
    """
    Full Book serializer with NESTED author details.

    Key concepts demonstrated:
    - Nested serializer (read-only author object in response)
    - source= to map a different field name
    - write_only field (author_id for writes)
    - SerializerMethodField for computed data
    - validate_() and validate() for validation
    - Custom create() and update()
    """

    # ── NESTED SERIALIZER (read) ──
    # When reading, show full author details as a nested object.
    # source='author' tells DRF which model attribute to serialize.
    # read_only=True means it won't be used for writes.
    author = AuthorMinimalSerializer(read_only=True)

    # ── WRITE FIELD ──
    # For creating/updating, the client sends author_id (a plain integer).
    # write_only=True means it appears in input but NOT in output.
    # source='author' links this field to the model's 'author' FK.
    author_id = serializers.PrimaryKeyRelatedField(
        queryset=Author.objects.all(),
        source='author',        # Maps to the 'author' FK on Book model
        write_only=True
    )

    # ── SerializerMethodField ──
    # Computed field — not on the model, calculated in get_*
    genre_display = serializers.SerializerMethodField()
    price_formatted = serializers.SerializerMethodField()

    class Meta:
        model = Book
        fields = [
            'id',
            'title',
            'author',           # Read: nested object
            'author_id',        # Write: integer FK
            'isbn',
            'genre',
            'genre_display',    # Computed: human-readable genre
            'published_year',
            'description',
            'price',
            'price_formatted',  # Computed: "$29.99" format
            'rating',
            'available',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_genre_display(self, obj):
        """get_display() is a Django method for choices fields."""
        return obj.get_genre_display()

    def get_price_formatted(self, obj):
        if obj.price is not None:
            return f'${obj.price:,.2f}'
        return 'Price not set'

    # ── FIELD-LEVEL VALIDATION ──
    def validate_isbn(self, value):
        """ISBN must be exactly 13 digits."""
        digits_only = value.replace('-', '').replace(' ', '')
        if not digits_only.isdigit():
            raise serializers.ValidationError('ISBN must contain only digits.')
        if len(digits_only) != 13:
            raise serializers.ValidationError('ISBN must be exactly 13 digits.')
        return digits_only  # Return normalized value

    def validate_rating(self, value):
        if value is not None and not (0.0 <= value <= 5.0):
            raise serializers.ValidationError('Rating must be between 0.0 and 5.0.')
        return value

    def validate_published_year(self, value):
        if value < 1000 or value > 2100:
            raise serializers.ValidationError(
                'Published year must be between 1000 and 2100.'
            )
        return value

    # ── CROSS-FIELD VALIDATION ──
    def validate(self, data):
        """
        validate() has access to ALL fields simultaneously.
        Perfect for cross-field rules.
        """
        price = data.get('price')
        rating = data.get('rating')

        # Example cross-field rule: highly rated books should have a price
        if rating and rating >= 4.5 and price is None:
            raise serializers.ValidationError(
                'Highly rated books (4.5+) must have a price listed.'
            )
        return data

    # ── CUSTOM create() ──
    # ModelSerializer provides a default create() that calls Model.objects.create()
    # Override when you need custom logic on creation.
    def create(self, validated_data):
        """
        validated_data is the cleaned dict from all validators.
        'author' key is already resolved to an Author instance
        because of source='author' on author_id field.
        """
        # You could add extra logic here:
        # - send a notification
        # - log the creation
        # - set fields based on the request user
        book = Book.objects.create(**validated_data)
        return book

    # ── CUSTOM update() ──
    def update(self, instance, validated_data):
        """
        instance = the existing Book object being updated.
        validated_data = the new values (only changed fields for PATCH).
        """
        # Update each field if provided (handles both PUT and PATCH)
        instance.title = validated_data.get('title', instance.title)
        instance.author = validated_data.get('author', instance.author)
        instance.isbn = validated_data.get('isbn', instance.isbn)
        instance.genre = validated_data.get('genre', instance.genre)
        instance.published_year = validated_data.get('published_year', instance.published_year)
        instance.description = validated_data.get('description', instance.description)
        instance.price = validated_data.get('price', instance.price)
        instance.rating = validated_data.get('rating', instance.rating)
        instance.available = validated_data.get('available', instance.available)
        instance.save()
        return instance


class BookListSerializer(serializers.ModelSerializer):
    """
    Lighter serializer for list views — fewer fields = faster response.
    Demonstrates using different serializers for list vs detail.
    """
    author_name = serializers.SerializerMethodField()
    genre_display = serializers.SerializerMethodField()

    class Meta:
        model = Book
        fields = [
            'id', 'title', 'author_name', 'genre_display',
            'published_year', 'price', 'rating', 'available'
        ]

    def get_author_name(self, obj):
        return obj.author.full_name

    def get_genre_display(self, obj):
        return obj.get_genre_display()