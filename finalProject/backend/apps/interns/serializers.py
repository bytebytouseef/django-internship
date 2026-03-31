from rest_framework import serializers
from apps.interns.models import Intern
from apps.users.serializers import UserSerializer

class InternSerializer(serializers.ModelSerializer):
    """Serializer for Intern model (list view)."""
    user = UserSerializer(read_only=True)
    assigned_mentor_email = serializers.CharField(source='assigned_mentor.email', read_only=True, required=False)

    class Meta:
        model = Intern
        fields = [
            'id', 'user', 'full_name', 'email', 'department', 
            'start_date', 'end_date', 'assigned_mentor_email', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class InternDetailSerializer(serializers.ModelSerializer):
    """Serializer for detailed Intern information."""
    user = UserSerializer(read_only=True)
    assigned_mentor = UserSerializer(read_only=True, required=False)

    class Meta:
        model = Intern
        fields = [
            'id', 'user', 'full_name', 'email', 'department', 'phone', 
            'date_of_birth', 'resume_url', 'skills', 'start_date', 'end_date',
            'assigned_mentor', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']


class InternCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating Intern profiles."""
    
    class Meta:
        model = Intern
        fields = [
            'full_name', 'email', 'department', 'phone', 'date_of_birth',
            'resume_url', 'skills', 'start_date', 'end_date', 'assigned_mentor'
        ]
