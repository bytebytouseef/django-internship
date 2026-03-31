from rest_framework import permissions

class IsAdmin(permissions.BasePermission):
    """Permission class to check if user is admin."""
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_admin)


class IsIntern(permissions.BasePermission):
    """Permission class to check if user has an intern profile."""
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return hasattr(request.user, 'intern_profile')


class IsOwnerOrAdmin(permissions.BasePermission):
    """Permission class to check if user is the owner or an admin."""
    def has_object_permission(self, request, view, obj):
        if request.user and request.user.is_admin:
            return True
        if hasattr(obj, 'user'):
            return obj.user == request.user
        return False


class IsReadOnlyOrAuthenticated(permissions.BasePermission):
    """Permission class for read-only or authenticated write access."""
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_authenticated)
