from rest_framework import serializers
from apps.assignments.models import Assignment, AssignmentSubmission
from apps.interns.serializers import InternSerializer
from apps.users.serializers import UserSerializer

class AssignmentSerializer(serializers.ModelSerializer):
    """Serializer for Assignment model (list view)."""
    assigned_to = serializers.PrimaryKeyRelatedField(
        queryset=Assignment._meta.get_field('assigned_to').remote_field.model.objects.all(),
        write_only=True
    )
    assigned_to_name = serializers.CharField(source='assigned_to.full_name', read_only=True)
    created_by_email = serializers.CharField(source='created_by.email', read_only=True)

    class Meta:
        model = Assignment
        fields = [
            'id', 'title', 'description', 'due_date', 'assigned_to',
            'assigned_to_name', 'created_by_email', 'status', 'created_at'
        ]
        read_only_fields = ['id', 'created_at', 'created_by_email', 'assigned_to_name']


class AssignmentDetailSerializer(serializers.ModelSerializer):
    """Serializer for detailed Assignment information."""
    assigned_to = InternSerializer(read_only=True)
    created_by = UserSerializer(read_only=True)

    class Meta:
        model = Assignment
        fields = ['id', 'title', 'description', 'due_date', 'assigned_to', 'created_by', 'status', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at']


class AssignmentSubmissionSerializer(serializers.ModelSerializer):
    """Serializer for Assignment Submission."""
    submitted_by_name = serializers.CharField(source='submitted_by.full_name', read_only=True)
    assignment_title = serializers.CharField(source='assignment.title', read_only=True)

    class Meta:
        model = AssignmentSubmission
        fields = [
            'id', 'assignment', 'assignment_title', 'submitted_by_name', 
            'submission_url', 'submission_text', 'status', 'reviewer_feedback',
            'submitted_at', 'created_at'
        ]
        read_only_fields = ['id', 'submitted_by', 'status', 'reviewer_feedback', 'submitted_at', 'created_at']


class AssignmentSubmissionDetailSerializer(serializers.ModelSerializer):
    """Serializer for detailed submission information."""
    assignment = AssignmentDetailSerializer(read_only=True)

    class Meta:
        model = AssignmentSubmission
        fields = [
            'id', 'assignment', 'submission_url', 'submission_text', 
            'status', 'reviewer_feedback', 'submitted_at', 'reviewed_at', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'submitted_at', 'created_at', 'updated_at']
