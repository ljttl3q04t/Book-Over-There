from services.managers.cache_manager import CACHE_CLUB_GET_MEMBERSHIP_INFOS, CACHE_CLUB_GET_MEMBER_INFOS, \
    simple_cache_data, \
    CACHE_CLUB_GET_INFOS_DICT
from services.models import User, Membership, BookClub, Member
from services.serializers import BookClubSerializer

def get_user_club(user: User):
    return Membership.objects.filter(member__user=user).values_list('book_club_id', flat=True)

@simple_cache_data(**CACHE_CLUB_GET_INFOS_DICT)
def get_clubs():
    result = BookClub.objects.all()
    serializer = BookClubSerializer(instance=result, many=True)
    return {item['id']: item for item in serializer.data}

def get_member_records(user_id=None, member_ids=None):
    return Member.objects.filter_ignore_none(
        user_id=user_id,
        id__in=member_ids,
    )

@simple_cache_data(**CACHE_CLUB_GET_MEMBER_INFOS)
def get_member_infos():
    members = get_member_records()
    result = {}
    for member in members:
        result[member.id] = {
            'full_name': member.full_name,
        }
    return result

@simple_cache_data(**CACHE_CLUB_GET_MEMBERSHIP_INFOS)
def get_membership_infos():
    memberships = get_membership_records()
    member_infos = get_member_infos()
    result = {}
    for membership in memberships:
        result[membership.id] = {
            'id': membership.id,
            'member': member_infos.get(membership.member_id)
        }
    return result

def get_membership_records(user=None, is_staff=None, membership_id=None):
    return Membership.objects \
        .filter(leaved_at=None) \
        .filter_ignore_none(member__user=user, is_staff=is_staff, id=membership_id)
