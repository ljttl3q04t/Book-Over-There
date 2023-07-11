import csv
from datetime import timedelta, datetime

from django.core.management import BaseCommand
from django.db import transaction
from django.utils import timezone

from services.models import BookCopy, MemberBookCopy, Membership, Member, BookClub, \
    MembershipOrder, MembershipOrderDetail

@transaction.atomic
def import_order_from_csv(file_path):
    with open(file_path, 'r') as csv_file:
        reader = csv.reader(csv_file)
        next(reader)  # Skip the header row

        current_time = timezone.now()
        today = datetime.now().date()
        club = BookClub.objects.get(name='D Free Book Cầu Giấy')
        new_order = None
        current_order = None
        for row in reader:
            _, index, book_name, book_code, full_name, _, _, _, order_status, _, day_count, _, _, _, _, _ = row
            print(index, book_name, book_code, full_name, order_status, day_count)
            member, _ = Member.objects.get_or_create(full_name=full_name)
            membership, _ = Membership.objects.get_or_create(book_club=club, member=member,
                                                             member_status=Membership.ACTIVE)
            book_copy = BookCopy.objects.filter(code=book_code, book_status=BookCopy.SHARING_CLUB).first()
            if not book_copy:
                print("error|book_not_found|{}|{}".format(book_name, book_code))
                continue
            member_book_copy = MemberBookCopy.objects.filter(book_copy=book_copy, current_reader=None).first()
            if not member_book_copy:
                print("error|member_book_copy_not_found|{}|{}".format(book_name, book_code))
                continue

            if index != new_order:
                new_order = index
                order_date = today - timedelta(days=int(day_count))
                current_order = MembershipOrder.objects.create(
                    membership=membership,
                    order_date=order_date,
                    confirm_date=order_date,
                    order_status=MembershipOrder.CONFIRMED,
                )

            due_date = current_order.order_date + timedelta(days=35)
            MembershipOrderDetail.objects.create(
                order=current_order,
                member_book_copy=member_book_copy,
                due_date=due_date,
            )

class Command(BaseCommand):
    help = "import order for d free book"

    def handle(self, *args, **options):
        import_order_from_csv('/home/tintin/Downloads/june.csv')
