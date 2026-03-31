from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from apps.assignments.models import Assignment, AssignmentSubmission
from apps.assignments.serializers import (
    AssignmentSerializer, AssignmentDetailSerializer,
    AssignmentSubmissionSerializer, AssignmentSubmissionDetailSerializer
)
from apps.assignments.permissions import IsAdminUser, IsInternUser, IsOwnerOrAdmin


class AssignmentViewSet(viewsets.ModelViewSet):
    """ViewSet for managing assignments."""
    queryset = Assignment.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'due_date']
    ordering = ['-created_at']
    filterset_fields = ['status', 'assigned_to']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return AssignmentDetailSerializer
        return AssignmentSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsAdminUser()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, IsInternUser])
    def submit(self, request, pk=None):
        """Submit work on an assignment."""
        assignment = self.get_object()
        try:
            intern = request.user.intern_profile
            if assignment.assigned_to != intern:
                return Response(
                    {'detail': 'Assignment not assigned to you'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Create or update submission
            submission, created = AssignmentSubmission.objects.get_or_create(
                assignment=assignment,
                submitted_by=intern,
                defaults={
                    'submission_url': request.data.get('submission_url', ''),
                    'submission_text': request.data.get('submission_text', ''),
                    'status': 'submitted'
                }
            )
            
            if not created:
                submission.submission_url = request.data.get('submission_url', submission.submission_url)
                submission.submission_text = request.data.get('submission_text', submission.submission_text)
                submission.save()
            
            assignment.status = 'submitted'
            assignment.save()
            
            serializer = AssignmentSubmissionSerializer(submission)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class AssignmentSubmissionViewSet(viewsets.ModelViewSet):
    """ViewSet for managing assignment submissions."""
    queryset = AssignmentSubmission.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]
    search_fields = ['assignment__title']
    ordering_fields = ['submitted_at']
    ordering = ['-submitted_at']
    filterset_fields = ['status', 'assignment']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return AssignmentSubmissionDetailSerializer
        return AssignmentSubmissionSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_admin:
            return AssignmentSubmission.objects.all()
        if hasattr(user, 'intern_profile'):
            return AssignmentSubmission.objects.filter(submitted_by=user.intern_profile)
        return AssignmentSubmission.objects.none()

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, IsAdminUser])
    def approve(self, request, pk=None):
        """Approve a submission."""
        submission = self.get_object()
        submission.status = 'approved'
        submission.reviewer_feedback = request.data.get('feedback', '')
        submission.reviewed_at = timezone.now()
        submission.save()
        
        submission.assignment.status = 'approved'
        submission.assignment.save()
        
        serializer = AssignmentSubmissionDetailSerializer(submission)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, IsAdminUser])
    def reject(self, request, pk=None):
        """Reject a submission."""
        submission = self.get_object()
        submission.status = 'rejected'
        submission.reviewer_feedback = request.data.get('feedback', 'Assignment rejected. Please revise and resubmit.')
        submission.reviewed_at = timezone.now()
        submission.save()
        
        submission.assignment.status = 'reviewed'
        submission.assignment.save()
        
        serializer = AssignmentSubmissionDetailSerializer(submission)
        return Response(serializer.data)
