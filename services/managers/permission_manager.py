from rest_framework.permissions import BasePermission

from services.managers.membership_manager import is_club_staff

class IsStaff(BasePermission):
    def has_permission(self, request, view):
        return is_club_staff(request.user.id, request.data.get('club_id'))

def is_club_admin(user):
    return user.is_staff and user.groups.filter(name='ClubAdmin').exists()

class IsClubAdmin(BasePermission):
    def has_permission(self, request, view):
        return is_club_admin(request.user)
