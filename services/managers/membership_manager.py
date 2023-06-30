from services.managers.cache_manager import simple_cache_data, CACHE_CLUB_GET_INFOS_DICT, CACHE_KEY_MEMBER_CLUB, \
    CACHE_KEY_MEMBER_INFOS
from services.models import User, Membership, BookClub, Member
from services.serializers import BookClubSerializer, MemberSerializer


def get_user_club(user: User):
    return Membership.objects.filter(member__user=user).values_list('book_club_id', flat=True)


@simple_cache_data(**CACHE_CLUB_GET_INFOS_DICT)
def get_clubs():
    result = BookClub.objects.all()
    serializer = BookClubSerializer(instance=result, many=True)
    return {item['id']: item for item in serializer.data}


@simple_cache_data(**CACHE_KEY_MEMBER_INFOS)
def get_member_infos():
    results = Member.objects.all()
    data = {}
    for item in results:
        item_infos = item.as_dict()
        data[item_infos['user']] = item_infos

    return data
    # return {item['id']: item.as_dict() for item in results}
