from rest_framework.permissions import BasePermission


def is_staff(user):
    return user.is_staff or user.groups.filter(name='Staff').exists()


class IsStaff(BasePermission):
    def has_permission(self, request, view):
        return is_staff(request.user)
