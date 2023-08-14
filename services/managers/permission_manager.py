from rest_framework.permissions import BasePermission

from services.managers.membership_manager import is_club_admin, is_club_staff

class IsStaff(BasePermission):
    def has_permission(self, request, view):
        return is_club_staff(request.user.id, request.data.get('club_id'))

class IsClubAdmin(BasePermission):
    def has_permission(self, request, view):
        return is_club_admin(request.user.id, request.data.get('club_id'))
