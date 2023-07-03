from django.core.management import BaseCommand
from django.utils import timezone

from services.managers import book_manager
from services.managers.crawl_manager import CrawTiki
from services.managers.email_manager import send_overdue_notification_email
from services.models import MembershipOrderDetail, BookCopy, Book, Member, Membership
from services.serializers import UserBorrowingBookSerializer

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

class Command(BaseCommand):

    def handle(self, *args, **options):
        test_send_email()
        # order_detail = MembershipOrderDetail.objects.get(id=18)
        # serializer = UserBorrowingBookSerializer(instance=order_detail)
        # data = serializer.to_representation(order_detail)
        # print(data)
