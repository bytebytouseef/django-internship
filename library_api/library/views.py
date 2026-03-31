from rest_framework import viewsets, generics, status, permissions
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication, SessionAuthentication
from rest_framework.permissions import (
    IsAuthenticated, IsAdminUser,
    IsAuthenticatedOrReadOnly, AllowAny
)
from django.shortcuts import get_object_or_404
from django.db.models import Q, Avg, Count

from .models import Author, Book
from .serializers import (
    AuthorSerializer, BookSerializer, BookListSerializer
)


# ============================================================
# PATTERN 1: @api_view — Function-Based API View
# Simple, explicit. Good for one-off endpoints.
# ============================================================

@api_view(['GET'])
@permission_classes([AllowAny])   # Per-view permission override
def api_overview(request):
    """
    Overview endpoint — public, no auth required.

    @api_view(['GET']) wraps the function so it:
    - Returns DRF Response (not Django HttpResponse)
    - Handles content negotiation (JSON vs browsable)
    - Parses request.data correctly
    - Enforces the listed HTTP methods only

    request.query_params — GET parameters (?search=python)
    request.data — POST/PUT/PATCH body
    """
    endpoints = {
        'overview': '/api/',
        'authors': {
            'list_create': '/api/authors/',
            'retrieve_update_delete': '/api/authors/{id}/',
        },
        'books': {
            'list_create': '/api/books/',
            'retrieve_update_delete': '/api/books/{id}/',
        },
        'auth': {
            'get_token': '/api/auth/token/',
            'register': '/api/auth/register/',
        },
        'stats': '/api/stats/',
        'search': '/api/search/?q=<term>',
    }
    return Response({
        'message': 'Library API — Welcome!',
        'version': '1.0',
        'endpoints': endpoints,
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
def api_stats(request):
    """Demonstrates aggregate queries exposed via API."""
    stats = {
        'total_books': Book.objects.count(),
        'total_authors': Author.objects.count(),
        'available_books': Book.objects.filter(available=True).count(),
        'average_rating': Book.objects.aggregate(avg=Avg('rating'))['avg'],
        'books_by_genre': list(
            Book.objects.values('genre').annotate(count=Count('id'))
        ),
    }
    return Response(stats)


@api_view(['GET'])
@permission_classes([AllowAny])
def search_books(request):
    """
    Search endpoint — demonstrates request.query_params.
    GET /api/search/?q=tolkien&genre=fantasy&available=true
    """
    # request.query_params is a QueryDict of URL parameters
    q = request.query_params.get('q', '')
    genre = request.query_params.get('genre', '')
    available = request.query_params.get('available', '')

    queryset = Book.objects.select_related('author').all()

    if q:
        queryset = queryset.filter(
            Q(title__icontains=q) |
            Q(author__first_name__icontains=q) |
            Q(author__last_name__icontains=q) |
            Q(description__icontains=q)
        )
    if genre:
        queryset = queryset.filter(genre=genre)
    if available.lower() == 'true':
        queryset = queryset.filter(available=True)

    # many=True — serialize a queryset (list) instead of a single object
    serializer = BookListSerializer(queryset, many=True)
    return Response({
        'count': queryset.count(),
        'results': serializer.data
    })


# ============================================================
# PATTERN 2: APIView — Class-Based View
# More structure than FBV. Implement get(), post(), etc. manually.
# ============================================================

class ManualBookListView(APIView):
    """
    Demonstrates APIView with manual method implementations.
    Note: We use ModelViewSet in production (Pattern 4),
    but this shows how everything works under the hood.

    Per-view auth override — overrides DEFAULT_AUTHENTICATION_CLASSES
    """
    authentication_classes = [TokenAuthentication, SessionAuthentication]
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request):
        """Handle GET /api/books-manual/ — public"""
        books = Book.objects.select_related('author').all()
        serializer = BookSerializer(
            books,
            many=True,
            # get_serializer_context equivalent — pass request for URL building
            context={'request': request}
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        """Handle POST /api/books-manual/ — authenticated only"""
        # request.data — parsed body (JSON, form data, etc.)
        serializer = BookSerializer(data=request.data)

        # is_valid() runs all field validators and validate_*() methods
        if serializer.is_valid():
            # save() calls our custom create() on the serializer
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        # serializer.errors — dict of field → [error messages]
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ============================================================
# PATTERN 3: Generic Views — Less boilerplate than APIView
# ============================================================

class BookListCreateGenericView(generics.ListCreateAPIView):
    """
    ListCreateAPIView handles:
    - GET → list all books
    - POST → create a book

    Provides get_queryset(), get_serializer_class(), etc. as hooks.
    """
    queryset = Book.objects.select_related('author').all()
    serializer_class = BookSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        """
        Override to add filtering.
        get_queryset() is called by the framework automatically.
        """
        qs = Book.objects.select_related('author').all()
        genre = self.request.query_params.get('genre')
        if genre:
            qs = qs.filter(genre=genre)
        return qs

    def get_serializer_context(self):
        """
        get_serializer_context() — pass extra data to the serializer.
        context is available inside serializer as self.context.
        """
        context = super().get_serializer_context()
        context['user'] = self.request.user
        return context

    def perform_create(self, serializer):
        """perform_create() — hook called by create() after validation."""
        serializer.save()


# ============================================================
# PATTERN 4: ModelViewSet — LEAST boilerplate, MOST powerful
# One class provides: list, create, retrieve, update, partial_update, destroy
# ============================================================

class AuthorViewSet(viewsets.ModelViewSet):
    """
    ModelViewSet automatically provides:
    - GET    /authors/          → list()
    - POST   /authors/          → create()
    - GET    /authors/{id}/     → retrieve()
    - PUT    /authors/{id}/     → update()
    - PATCH  /authors/{id}/     → partial_update()
    - DELETE /authors/{id}/     → destroy()

    All 6 actions from a single class!
    """
    queryset = Author.objects.prefetch_related('books').all()
    serializer_class = AuthorSerializer

    # Per-view auth/permission override
    # Overrides DEFAULT_AUTHENTICATION_CLASSES for this ViewSet only
    authentication_classes = [TokenAuthentication, SessionAuthentication]
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        """
        Override for filtering support.
        ?nationality=British&name=tolkien
        """
        qs = Author.objects.prefetch_related('books').all()
        nationality = self.request.query_params.get('nationality')
        name = self.request.query_params.get('name')

        if nationality:
            qs = qs.filter(nationality__icontains=nationality)
        if name:
            qs = qs.filter(
                Q(first_name__icontains=name) |
                Q(last_name__icontains=name)
            )
        return qs

    def get_serializer_context(self):
        """Pass request to serializer so it can build absolute URLs."""
        return {'request': self.request, 'format': self.format_kwarg, 'view': self}

    def destroy(self, request, *args, **kwargs):
        """
        Override destroy to add a custom response message instead of 204.
        Default ModelViewSet.destroy() returns 204 No Content.
        """
        instance = self.get_object()
        name = str(instance)
        book_count = instance.books.count()
        self.perform_destroy(instance)
        return Response(
            {
                'message': f'Author "{name}" deleted successfully.',
                'books_also_deleted': book_count
            },
            status=status.HTTP_200_OK
        )


class BookViewSet(viewsets.ModelViewSet):
    """
    Full CRUD for Books via ModelViewSet.
    Demonstrates:
    - Different serializers for list vs detail
    - Filtering via get_queryset()
    - Custom action responses
    """
    queryset = Book.objects.select_related('author').all()
    authentication_classes = [TokenAuthentication, SessionAuthentication]
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_serializer_class(self):
        """
        Return different serializers for list vs detail views.
        self.action can be: 'list', 'create', 'retrieve', 'update',
                            'partial_update', 'destroy'
        """
        if self.action == 'list':
            return BookListSerializer   # Lightweight for lists
        return BookSerializer           # Full detail for single objects

    def get_queryset(self):
        """
        Comprehensive filtering via query params.
        GET /api/books/?genre=fiction&available=true&author=1&min_rating=4
        """
        qs = Book.objects.select_related('author').all()

        genre = self.request.query_params.get('genre')
        available = self.request.query_params.get('available')
        author_id = self.request.query_params.get('author')
        min_rating = self.request.query_params.get('min_rating')
        year = self.request.query_params.get('year')

        if genre:
            qs = qs.filter(genre=genre)
        if available is not None:
            qs = qs.filter(available=available.lower() == 'true')
        if author_id:
            qs = qs.filter(author_id=author_id)
        if min_rating:
            qs = qs.filter(rating__gte=float(min_rating))
        if year:
            qs = qs.filter(published_year=year)

        return qs

    def create(self, request, *args, **kwargs):
        """Override create for custom 201 response."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)   # Auto-returns 400 if invalid
        self.perform_create(serializer)
        return Response(
            {
                'message': 'Book created successfully!',
                'book': serializer.data
            },
            status=status.HTTP_201_CREATED
        )

    def perform_create(self, serializer):
        serializer.save()


# ============================================================
# AUTH VIEWS
# ============================================================

@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    """
    Register a new user and return their auth token.
    Demonstrates: manual user creation + token generation.
    """
    from django.contrib.auth.models import User
    from rest_framework.authtoken.models import Token

    username = request.data.get('username')
    password = request.data.get('password')
    email = request.data.get('email', '')

    if not username or not password:
        return Response(
            {'error': 'Username and password are required.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    if User.objects.filter(username=username).exists():
        return Response(
            {'error': 'Username already taken.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    user = User.objects.create_user(username=username, password=password, email=email)

    # Token.objects.create() — generates a unique token for the user
    token, created = Token.objects.get_or_create(user=user)

    return Response(
        {
            'message': 'User registered successfully!',
            'user': {'id': user.id, 'username': user.username},
            'token': token.key   # The client stores this and sends it on every request
        },
        status=status.HTTP_201_CREATED
    )