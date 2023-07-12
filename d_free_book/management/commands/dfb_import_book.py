import csv

from django.core.management import BaseCommand
from django.db import transaction
from django.utils import timezone

from d_free_book.models import ClubBook
from services.models import User, Book, Author, Category, BookCopy, MemberBookCopy, Membership, BookClub

@transaction.atomic
def import_books_from_csv(file_path):
    with open(file_path, 'r') as csv_file:
        reader = csv.reader(csv_file)
        next(reader)  # Skip the header row

        current_time = timezone.now()
        # user = User.objects.get(username='d_free_book_caugiay')
        # membership = Membership.objects.get(member__user=user)
        club = BookClub.objects.get(name='D Free Book Cầu Giấy')
        for row in reader:
            index, code, name, category, author, init_count, current_count, \
            count_2022, count_2023, note = row
            if not name or note or not init_count or not current_count:
                continue

            author_record, _ = Author.objects.get_or_create(name=author)
            category_record, _ = Category.objects.get_or_create(name=category)
            book_record, _ = Book.objects.get_or_create(name=name, author=author_record, category=category_record)
            club_book, _ = ClubBook.objects.get_or_create(book=book_record,club=club,code=code,init_count=int(init_count), current_count=int(current_count))
            # count_book_copy = BookCopy.objects.filter(book=book_record, user=user).count()
            # for i in range(int(init_count) - count_book_copy):
            #     book_copy = BookCopy.objects \
            #         .create(book=book_record, user=user, book_status=BookCopy.SHARING_CLUB, code=code)
            #     member_book_copy = MemberBookCopy.objects \
            #         .create(book_copy=book_copy, membership=membership, onboard_date=current_time)

            print("import book: ", name)

class Command(BaseCommand):
    help = "import book for d free book"

    def handle(self, *args, **options):
        import_books_from_csv('/home/caugiay.csv')
