from rest_framework.permissions import BasePermission

class HasRole(BasePermission):
    required_roles = []

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if not self.required_roles:
            return True
        return request.user.role in self.required_roles

def role_permission(*roles):
    class _P(HasRole):
        required_roles = list(roles)
    return _P

class IsSelf(BasePermission):
    # For endpoints where user_id is path param
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        user_id = view.kwargs.get("user_id") or view.kwargs.get("pk")
        if not user_id:
            return False
        return str(request.user.id) == str(user_id) or request.user.role in ("ADMIN",)
