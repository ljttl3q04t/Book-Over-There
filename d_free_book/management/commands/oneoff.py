from django.core.management import BaseCommand
from django.db.models import Count
from django.db.models.functions import TruncMonth

from d_free_book.manager import gen_report, get_order_detail_records
from d_free_book.models import DFreeOrderDetail, ClubBook
from django.db import connection
from django.db.models import F
from django.db import connection

class Command(BaseCommand):
    def handle(self, *args, **options):
        data = get_order_detail_records(order_detail_ids=[5639, 5640]).values('club_book_id', 'order_id')
        print(data)
