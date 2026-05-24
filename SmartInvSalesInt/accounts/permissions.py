from rest_framework.permissions import BasePermission

class IsManagerOrAbove(BasePermission):
    def has_permission(self, request, view):
        user = request.user

        if not user or not user.is_authenticated:
            return False
        
        role = user.userprofile.role
        return role is ["owner", "manager","supervisor"]
    