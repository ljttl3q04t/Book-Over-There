from services.models import User, Membership


def get_user_club(user: User):
    return Membership.objects.filter(member__user=user).values_list('book_club_id', flat=True)
