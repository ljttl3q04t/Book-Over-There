from django.core.management import BaseCommand
from django.db.models import Count
from django.db.models.functions import TruncMonth

from d_free_book.manager import gen_report, get_order_detail_records
from d_free_book.models import DFreeOrder, DFreeOrderDetail, ClubBook, DFreeMember, DFreeDraftOrder
from django.db import connection, transaction
from django.db.models import F
from django.db import connection

from services.models import User

@transaction.atomic
def clean_data_by_phone_number(phone_number):
    member = DFreeMember.objects.filter(phone_number=phone_number).first()
    if member:
        member.phone_number = None
        member.save()

    user = User.objects.filter(phone_number=phone_number).first()
    if not user:
        return

    user.phone_number = None
    user.is_verify = False
    user.save()
    member_ids = DFreeMember.objects.filter(user_id=user.id).flat_list('id')
    order_ids = DFreeOrder.objects.filter(member_id__in=member_ids).flat_list('id')
    order_detail_ids = DFreeOrderDetail.objects.filter(order_id__in=order_ids).flat_list('id')
    draft_order_ids = DFreeDraftOrder.objects.filter(user_id=user.id).flat_list('id')

    DFreeDraftOrder.objects.filter(id__in=draft_order_ids).delete()
    DFreeOrderDetail.objects.filter(id__in=order_detail_ids).delete()
    DFreeOrder.objects.filter(id__in=order_ids).delete()
    DFreeMember.objects.filter(id__in=member_ids).delete()

class Command(BaseCommand):
    def handle(self, *args, **options):
        clean_data_by_phone_number('0336317198')
