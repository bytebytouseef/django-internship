from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    password2 = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
        label='Confirm Password'
    )

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'password', 'password2']
        read_only_fields = ['id']
        extra_kwargs = {'email': {'required': True}}

    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError({'password': 'Passwords do not match.'})
        return data

    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(**validated_data)
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    order_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name',
                  'date_joined', 'order_count']
        read_only_fields = ['id', 'username', 'date_joined']

    def get_order_count(self, obj):
        return obj.orders.count()


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Extends the default JWT serializer to add custom claims to the token payload.

    JWT Structure:
    ┌──────────────┬─────────────────────────────┬───────────────────┐
    │   HEADER     │          PAYLOAD             │     SIGNATURE     │
    │  algorithm   │  user_id, username, exp,     │  HMAC-SHA256 of   │
    │  token type  │  iat, jti + our custom data  │  header + payload │
    └──────────────┴─────────────────────────────┴───────────────────┘

    The payload (claims) is BASE64 decoded — NOT encrypted!
    Never put sensitive data in JWT claims.

    Access token: short-lived (15 min), used for API requests
    Refresh token: long-lived (7 days), used to obtain new access tokens
    """

    @classmethod
    def get_token(cls, user):
        """
        get_token() adds custom data to the JWT PAYLOAD.
        These claims are embedded in the token itself —
        no database lookup needed to read them.
        """
        token = super().get_token(user)

        # Custom claims — added to the JWT payload
        token['username'] = user.username
        token['email'] = user.email
        token['is_staff'] = user.is_staff
        token['full_name'] = f'{user.first_name} {user.last_name}'.strip()

        return token

    def validate(self, attrs):
        """
        validate() returns the token pair dict.
        We add user info to the login response body.
        """
        data = super().validate(attrs)

        # Add extra user info to the response body (not the token)
        data['user'] = {
            'id': self.user.id,
            'username': self.user.username,
            'email': self.user.email,
            'is_staff': self.user.is_staff,
        }
        data['message'] = 'Login successful.'
        return data