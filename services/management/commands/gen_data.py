import datetime

import requests
from bs4 import BeautifulSoup
from django.core.management import BaseCommand
from django.db import transaction
from django.utils import timezone

from services.models import Category, Book, BookCopy, User, MemberBookCopy, Membership


class Command(BaseCommand):
    help = "crawl books from fahasa and store to database"

    def handle(self, *args, **options):
        user = User.objects.get(username='chv_admin')
        membership = Membership.objects.get(member__user=user)
        book_copys = BookCopy.objects.filter(user=user)
        current_time = timezone.now()
        member_book_copys = [MemberBookCopy(book_copy=book_copy, membership=membership, onboard_date=current_time) for
                             book_copy in book_copys]

        MemberBookCopy.objects.bulk_create(member_book_copys)

        # category = Category.objects.get(name='Tiểu Sử Hồi Ký')
        # books = Book.objects.filter(category=category)
        # book_copys = [BookCopy(book=book, user=user, book_status=BookCopy.SHARING_CLUB) for book in books]
        # with transaction.atomic():
        #     x = BookCopy.objects.bulk_create(book_copys)
        #     print(x)
