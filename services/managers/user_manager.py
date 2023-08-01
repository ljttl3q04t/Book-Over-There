from services.models import User

def get_user_records(phone_number=None, is_verify=None):
    return User.objects.filter_ignore_none(
        phone_number=phone_number,
        is_verify=is_verify,
    )
