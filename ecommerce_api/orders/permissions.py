from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsOrderOwner(BasePermission):
    """
    Object-level permission for orders.
    Users can only view and modify their own orders.
    Admins can access all orders.
    """
    message = 'You can only access your own orders.'

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        """
        obj is the Order instance.
        DRF calls this automatically when the view uses get_object().
        """
        if request.user.is_staff:
            return True
        return obj.user == request.user