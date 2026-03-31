from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from apps.interns.models import Intern
from apps.interns.serializers import InternSerializer, InternDetailSerializer, InternCreateSerializer
from apps.interns.permissions import IsOwner, IsAdminUser, IsInternUser

class InternViewSet(viewsets.ModelViewSet):
    """ViewSet for managing intern profiles."""
    queryset = Intern.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['full_name', 'email', 'department']
    ordering_fields = ['created_at', 'full_name']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return InternDetailSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return InternCreateSerializer
        return InternSerializer

    def get_permissions(self):
        if self.action == 'me':
            return [IsAuthenticated()]
        elif self.action in ['update', 'partial_update']:
            return [IsAuthenticated(), IsOwner()]
        return [IsAuthenticated()]

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def me(self, request):
        """Get current logged-in intern's profile."""
        try:
            intern = request.user.intern_profile
            serializer = InternDetailSerializer(intern)
            return Response(serializer.data)
        except Intern.DoesNotExist:
            return Response(
                {'detail': 'Intern profile not found'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=False, methods=['put'], permission_classes=[IsAuthenticated])
    def me_update(self, request):
        """Update current logged-in intern's profile."""
        try:
            intern = request.user.intern_profile
            serializer = InternDetailSerializer(intern, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Intern.DoesNotExist:
            return Response(
                {'detail': 'Intern profile not found'},
                status=status.HTTP_404_NOT_FOUND
            )
