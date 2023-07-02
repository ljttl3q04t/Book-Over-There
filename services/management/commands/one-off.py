from django.core.management import BaseCommand

from services.managers import book_manager
from services.managers.crawl_manager import CrawTiki
from services.models import MembershipOrderDetail, BookCopy, Book
from services.serializers import UserBorrowingBookSerializer

def fixBookImage():
    book_ids = BookCopy.objects.all().values_list('book_id', flat=True)
    books = Book.objects.filter(id__in=book_ids)
    for book in books:
        image_url = str(book.image)
        if 'fahasa.com' in image_url:
            print('save book: ', book.name, image_url)
            book_manager.save_image_from_url(book, image_url)

class Command(BaseCommand):

    def handle(self, *args, **options):
        order_detail = MembershipOrderDetail.objects.get(id=18)
        serializer = UserBorrowingBookSerializer(instance=order_detail)
        data = serializer.to_representation(order_detail)
        print(data)
