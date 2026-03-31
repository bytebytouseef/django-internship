from rest_framework import permissions

class IsAdminUser(permissions.BasePermission):
    """Permission class to check if user is admin."""
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_admin)


class IsInternUser(permissions.BasePermission):
    """Permission class to check if user has intern profile."""
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return hasattr(request.user, 'intern_profile')


class IsOwnerOrAdmin(permissions.BasePermission):
    """Permission to check if user owns the submission or is admin."""
    def has_object_permission(self, request, view, obj):
        if request.user and request.user.is_admin:
            return True
        if hasattr(obj, 'submitted_by'):
            return obj.submitted_by.user == request.user
        return False
