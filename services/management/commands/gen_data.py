import datetime

import requests
from bs4 import BeautifulSoup
from django.core.management import BaseCommand
from django.db import transaction
from django.utils import timezone

from services.models import Category, Book, BookCopy, User, MemberBookCopy, Membership
from services.managers.membership_manager import get_clubs, get_member_infos
from django.core.cache import cache
from django.db import connection

class Command(BaseCommand):
    help = "crawl books from fahasa and store to database"

    def handle(self, *args, **options):
        cache.clear()
        members = get_member_infos()
        print(members)
        print("query: ")
        print(connection.queries)


