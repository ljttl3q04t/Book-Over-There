from django.utils import timezone
from twilio.rest import Client

from services.models import OTP
import random
import string
import os

OTP_FROM_NUMBER = '+14706002595'
OTP_MESSAGE = 'Your Book Over There code is: {otp_code}'

class OtpClient:
    _client = None

    @classmethod
    def get_client(cls):
        if cls._client is None:
            cls._instance = cls._create_instance()
        return cls._instance

    @classmethod
    def _create_instance(cls):
        account_sid = os.environ.get("TWILIO_ACCOUNT_SID")
        auth_token = os.environ.get("TWILIO_AUTH_TOKEN")
        return Client(account_sid, auth_token)


def get_otp_records(phone_number=None, enable=None, otp_code=None):
    return OTP.objects.filter_ignore_none(
        phone_number=phone_number,
        enable=enable,
        otp_code=otp_code
    )

def send_otp(otp):
    otp_client = OtpClient.get_client()
    phone_number = '+84' + otp.phone_number[1:]
    message = otp_client.messages.create(
        body=OTP_MESSAGE.format(otp_code=otp.otp_code),
        from_=OTP_FROM_NUMBER,
        to=phone_number,
    )
    otp.message_sid = message.sid
    otp.save()

def check_message_status(message_sid):
    otp_client = OtpClient.get_client()
    message = otp_client.messages(message_sid).fetch()
    return message.status

def remove_expired_otp(phone_number):
    return get_otp_records(phone_number=phone_number, enable=True) \
        .filter(expiry_date__lt=timezone.now() - timezone.timedelta(minutes=OTP.OTP_EXPIRY_LENGTH)) \
        .update(enable=False)

def generate_otp(phone_number):
    if get_otp_records(phone_number=phone_number, enable=True).exists():
        return None, 'OTP exists'
    otp_code = ''.join(random.choices(string.digits, k=OTP.OTP_CODE_LENGTH))
    expiry_date = timezone.now() + timezone.timedelta(minutes=OTP.OTP_EXPIRY_LENGTH)
    otp = OTP.objects.create(
        phone_number=phone_number,
        otp_code=otp_code,
        expiry_date=expiry_date,
        enable=True,
    )
    return otp, None

def verify_otp_code(phone_number, otp_code):
    current_otp = get_otp_records(phone_number=phone_number, otp_code=otp_code, enable=True).first()
    if not current_otp:
        return False, 'otp not exists'
    if current_otp.expiry_date < timezone.now():
        return False, 'otp expired'
    return True, None

