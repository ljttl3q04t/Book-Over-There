from rest_framework.permissions import BasePermission

def is_staff(user):
    return user.is_staff or user.groups.filter(name='Staff').exists()

class IsStaff(BasePermission):
    def has_permission(self, request, view):
        return is_staff(request.user)

def is_club_admin(user):
    return user.is_staff and user.groups.filter(name='ClubAdmin').exists()

class isClubAdmin(BasePermission):
    def has_permission(self, request, view):
        return is_club_admin(request.user)
