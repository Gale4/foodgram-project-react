from rest_framework import permissions

class IsOwnerOrReadOnly(permissions.IsAuthenticatedOrReadOnly):
    """Разрешение для автора и администратора."""
    
    def has_object_permission(self, request, view, obj):
        return (request.method in permissions.SAFE_METHODS
                or (request.user == obj.author)
                or request.user.is_staff)