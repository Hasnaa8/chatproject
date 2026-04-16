from rest_framework import permissions

class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # 1. Allow any user to see the profile (GET, HEAD, OPTIONS)
        if request.method in permissions.SAFE_METHODS:
            return True

        # 2. For POST, PUT, PATCH, DELETE: Must be the owner
        return obj.user == request.user