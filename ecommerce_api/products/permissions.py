from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAdminOrReadOnly(BasePermission):
    """
    Custom permission extending BasePermission.

    has_permission() — checks EVERY request before it reaches the view.
    Returns True = allow, False = deny (403).

    SAFE_METHODS = ('GET', 'HEAD', 'OPTIONS') — read-only operations.
    """
    message = 'Only admin users can modify products.'

    def has_permission(self, request, view):
        # Allow all read operations
        if request.method in SAFE_METHODS:
            return True
        # Write operations require admin
        return request.user and request.user.is_staff


class IsOwnerOrAdmin(BasePermission):
    """
    Object-level permission — controls access to INDIVIDUAL records.

    has_object_permission() — called only if has_permission() passes.
    It receives the specific object being accessed.

    Use case: users can only edit/delete their own orders.
    """
    message = 'You do not have permission to access this resource.'

    def has_permission(self, request, view):
        # Must be authenticated for any access
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        """
        obj = the specific Order/Product instance being accessed.

        This is called by get_object() inside the view.
        The view must call self.check_object_permissions(request, obj).
        Generic views and ViewSets do this automatically.
        """
        # Admins can access everything
        if request.user.is_staff:
            return True

        # Check ownership — obj.user for orders
        if hasattr(obj, 'user'):
            return obj.user == request.user

        # Check created_by for products
        if hasattr(obj, 'created_by'):
            return obj.created_by == request.user

        return False


class IsOwnerOrReadOnly(BasePermission):
    """
    Allow anyone to read, but only the owner can write.
    Combines read-access with object-level ownership check.
    """
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # Safe methods always allowed
        if request.method in SAFE_METHODS:
            return True
        # Write methods only for owner or admin
        if request.user.is_staff:
            return True
        if hasattr(obj, 'user'):
            return obj.user == request.user
        if hasattr(obj, 'created_by'):
            return obj.created_by == request.user
        return False