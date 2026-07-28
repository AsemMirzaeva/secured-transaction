from rest_framework.permissions import BasePermission


class IsOperator(BasePermission):
   
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and (request.user.is_staff or getattr(request.user, "is_operator", False))
        )


class IsOwner(BasePermission):
   
    def has_object_permission(self, request, view, obj):
        owner = getattr(obj, "user", None) or getattr(obj, "owner", None)
        return owner == request.user