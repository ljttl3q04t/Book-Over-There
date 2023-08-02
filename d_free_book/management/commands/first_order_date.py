from django.core.management import BaseCommand

from d_free_book.models import DFreeMember, DFreeOrder

class Command(BaseCommand):
    def handle(self, *args, **options):
        for member in DFreeMember.objects.all():
            order = DFreeOrder.objects.filter(member=member).order_by('order_date').first()
            if order:
                member.first_order_date = order.order_date
                member.save()
                print(member.id, order.id, order.order_date)

