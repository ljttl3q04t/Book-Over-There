from django.core.management import BaseCommand
from django.db.models import Count
from django.db.models.functions import TruncMonth

from d_free_book.manager import gen_report
from d_free_book.models import DFreeOrderDetail
from django.db import connection

class Command(BaseCommand):
    def handle(self, *args, **options):
        # a = gen_report(4)
        # print(a)
        order_detail_by_month = DFreeOrderDetail.objects.filter(order__club_id=4) \
            .annotate(month=TruncMonth('order__order_date')) \
            .values('month') \
            .annotate(total_books=Count('id')) \
            .order_by('month')

        print(order_detail_by_month)
        print(connection.queries)
