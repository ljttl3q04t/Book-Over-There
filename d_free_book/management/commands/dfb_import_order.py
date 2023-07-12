import csv
from datetime import timedelta, datetime

from django.core.management import BaseCommand
from django.db import transaction
from django.utils import timezone

from d_free_book.models import DFreeMember, ClubBook, DFreeOrder, DFreeOrderDetail
from services.models import BookClub, \
    MembershipOrder

@transaction.atomic
def import_order_from_csv(file_path):
    with open(file_path, 'r') as csv_file:
        reader = csv.reader(csv_file)
        next(reader)  # Skip the header row

        today = datetime.now().date()
        new_order = None
        current_order = None
        for row in reader:
            _, index, book_name, book_code, full_name, _, name_code, _, order_status, _, day_count, _, _, _, _, _ = row
            print(index, book_name, book_code, full_name, name_code, order_status, day_count)

            club_book = ClubBook.objects.filter(code=book_code).first()
            if not club_book:
                print("error|book_not_found|{}|{}".format(book_name, book_code))
                continue

            dfb_member, _ = DFreeMember.objects.get_or_create(code=name_code, full_name=full_name)
            if index != new_order:
                new_order = index
                order_date = today - timedelta(days=int(day_count))
                due_date = order_date + timedelta(days=35)
                current_order = DFreeOrder.objects.create(
                    member=dfb_member,
                    order_date=order_date,
                    due_date=due_date,
                    order_status=MembershipOrder.CONFIRMED,
                )

            DFreeOrderDetail.objects.create(
                order=current_order,
                club_book=club_book,
            )

class Command(BaseCommand):
    help = "import order for d free book"

    def handle(self, *args, **options):
        import_order_from_csv('/home/june.csv')
