from django.core.management import BaseCommand
from django.utils import timezone

from services.managers import book_manager
from services.managers.book_manager import get_book_infos, get_book_records
from services.managers.crawl_manager import CrawTiki
from services.managers.email_manager import send_overdue_notification_email
from services.models import MembershipOrderDetail, BookCopy, Book, Member, Membership, Author
from services.serializers import UserBorrowingBookSerializer, CustomImageField
from django.db import connection
from rest_framework import serializers

def fixBookImage():
    book_ids = BookCopy.objects.all().values_list('book_id', flat=True)
    books = Book.objects.filter(id__in=book_ids)
    for book in books:
        image_url = str(book.image)
        if 'fahasa.com' in image_url:
            print('save book: ', book.name, image_url)
            book_manager.save_image_from_url(book, image_url)

def test_send_email():
    membership = Membership.objects.get(id=3)
    book_title = "Nha Gia Kim"
    due_date = timezone.now()
    send_overdue_notification_email(membership, book_title, due_date)

class OneOffSerializer(serializers.Serializer):
    image = CustomImageField(required=False)

def test_one_off():
    # author_ids = set(Book.objects.flat_list('author_id', distinct=True))
    # remove_author_ids = Author.objects.exclude(id__in=author_ids).flat_list('id')
    # print(remove_author_ids)
    # print(len(remove_author_ids))
    book_ids = get_book_records().order_by('-id')[:200].pk_list()
    # book_ids = get_book_records(book_ids=[12300, 12301]).order_by('-id')[:2].pk_list()
    # print(book_ids)
    book_infos = get_book_infos(book_ids)
    for q in connection.queries:
        print(q)
    # for book in book_infos.values():
    #     print(book)
        # s = OneOffSerializer(data=book)
        # if s.is_valid():
        #     print(s.data)

    # book = {'name': 'Book Name', 'image': None}  # Example book data with 'image' attribute set to None
    # serializer = OneOffSerializer(data=book)
    # print(serializer.is_valid())
    #
    # serialized_data = serializer.data
    # print(serialized_data)  # {'image': None, ...}

class Command(BaseCommand):

    def handle(self, *args, **options):
        test_one_off()
        # test_send_email()
        # order_detail = MembershipOrderDetail.objects.get(id=18)
        # serializer = UserBorrowingBookSerializer(instance=order_detail)
        # data = serializer.to_representation(order_detail)
        # print(data)
