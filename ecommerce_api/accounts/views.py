from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView
from rest_framework_simplejwt.tokens import RefreshToken
from drf_spectacular.utils import extend_schema
from django.contrib.auth.models import User

from .serializers import RegisterSerializer, UserProfileSerializer, CustomTokenObtainPairSerializer


@extend_schema(summary='Register a new user', tags=['Auth'])
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Generate JWT tokens on registration
        refresh = RefreshToken.for_user(user)
        return Response({
            'message': 'Registration successful!',
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
            },
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        }, status=status.HTTP_201_CREATED)


@extend_schema(
    summary='Login — obtain JWT access + refresh tokens',
    tags=['Auth'],
    description="""
    Returns access token (15 min) and refresh token (7 days).
    
    **Access Token**: Send as `Authorization: Bearer <access_token>` on every request.
    **Refresh Token**: Send to `/api/v1/auth/token/refresh/` to get a new access token.
    
    JWT Payload structure (decoded):
```json
    {
        "token_type": "access",
        "exp": 1234567890,
        "iat": 1234567890,
        "jti": "unique-id",
        "user_id": 1,
        "username": "john",
        "email": "john@example.com",
        "is_staff": false
    }
```
    """
)
class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Extends TokenObtainPairView to use our custom serializer.
    The serializer adds username, email, is_staff to the JWT payload
    and returns user info in the response body.
    """
    serializer_class = CustomTokenObtainPairSerializer


@extend_schema(summary='Refresh access token', tags=['Auth'])
class CustomTokenRefreshView(TokenRefreshView):
    """
    POST refresh token → get new access token (and new refresh token if ROTATE_REFRESH_TOKENS=True).
    The old refresh token is blacklisted after rotation.
    """
    pass


@extend_schema(summary='Verify token validity', tags=['Auth'])
class CustomTokenVerifyView(TokenVerifyView):
    """POST an access token to verify it's still valid."""
    pass


@extend_schema(summary='Logout — blacklist refresh token', tags=['Auth'])
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        Blacklist the refresh token to invalidate the session.
        The access token can't be revoked (it's stateless) — it expires on its own.
        This is why short ACCESS_TOKEN_LIFETIME is important.
        """
        try:
            refresh_token = request.data.get('refresh')
            if not refresh_token:
                return Response({'error': 'Refresh token required.'}, status=status.HTTP_400_BAD_REQUEST)
            token = RefreshToken(refresh_token)
            token.blacklist()  # Adds to the token_blacklist table
            return Response({'message': 'Logged out successfully.'})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(summary='Get/update current user profile', tags=['Auth'])
class ProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user