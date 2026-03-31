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


class IsOwner(permissions.BasePermission):
    """Permission to check if user is the owner of the intern profile."""
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user
