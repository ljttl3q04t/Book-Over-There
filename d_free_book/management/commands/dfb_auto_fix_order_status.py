from django.core.management import BaseCommand
from django.db import transaction

@transaction.atomic
def auto_fix_order():


class Command(BaseCommand):
    help = "auto fix order status"

    def handle(self, *args, **options):
        auto_fix_order()
