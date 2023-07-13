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
        club = BookClub.objects.get(code='dfb_daila')
        for row in reader:
            index, code, _, name, category, author, note, init_count, _, current_count, _, _, _, _ = row
            if not name or not author or note or not init_count or not current_count:
                continue

            print(code, name, author, category, init_count, current_count)
            author_record, _ = Author.objects.get_or_create(name=author)
            category_record, _ = Category.objects.get_or_create(name=category)
            book_record, _ = Book.objects.get_or_create(name=name, author=author_record, category=category_record)
            club_book, _ = ClubBook.objects.get_or_create(book=book_record,club=club,code=code,init_count=int(init_count), current_count=int(current_count))

            print("import book: ", name)

class Command(BaseCommand):
    help = "import book for d free book"

    def handle(self, *args, **options):
        import_books_from_csv('/home/daila.csv')
