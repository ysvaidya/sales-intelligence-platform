from rest_framework.permissions import BasePermission

class InvenotoryAccessPermission(BasePermission):

    message = (
        "You are not allowed to access inventory movements."
    )

    ALLOWED_ROLES = (
        "owner",
        "manager",
        "supervisor"
    )

    def has_permission(self, request, view):

        user = request.user

        if not user.is_authenticated:
            return False
        
        profile = getattr(user,"userprofile", None)

        if not profile:
            return False
        
        return profile.role in self.ALLOWED_ROLES