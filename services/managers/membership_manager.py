from services.managers.cache_manager import simple_cache_data, CACHE_CLUB_GET_INFOS_DICT, CACHE_KEY_MEMBER_INFOS, \
    combine_key_cache_data
from services.models import User, Membership, BookClub, Member
from services.serializers import BookClubSerializer

def get_user_club(user: User):
    return Membership.objects.filter(member__user=user).values_list('book_club_id', flat=True)

@simple_cache_data(**CACHE_CLUB_GET_INFOS_DICT)
def get_clubs():
    result = BookClub.objects.all()
    serializer = BookClubSerializer(instance=result, many=True)
    return {item['id']: item for item in serializer.data}

def get_member_records(user_id=None):
    return Member.objects.filter_ignore_none(
        user_id=user_id,
    )

def get_membership_records(user=None, is_staff=None):
    return Membership.objects \
        .filter(leaved_at=None) \
        .filter_ignore_none(member__user=user, is_staff=is_staff)

@combine_key_cache_data(**CACHE_KEY_MEMBER_INFOS)
def get_member_infos():
    results = Member.objects.all()
    data = {}
    for item in results:
        item_infos = item.as_dict()
        data[item_infos['user']] = item_infos

    return data
    # return {item['id']: item.as_dict() for item in results}

def get_membership_by_user(user):
    return Membership.objects.filter(member__user=user, leaved_at=None)
