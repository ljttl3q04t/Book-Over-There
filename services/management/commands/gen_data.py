from django.core.cache import cache
from django.core.management import BaseCommand
from django.db import connection

from services.managers.membership_manager import get_member_infos

class Command(BaseCommand):
    help = "crawl books from fahasa and store to database"

    def handle(self, *args, **options):
        cache.clear()
        members = get_member_infos()
        print(members)
        print("query: ")
        print(connection.queries)
