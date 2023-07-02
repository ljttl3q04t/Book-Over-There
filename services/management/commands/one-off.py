from django.core.management import BaseCommand

from services.managers.crawl_manager import CrawTiki

class Command(BaseCommand):

    def handle(self, *args, **options):
        x = CrawTiki('https://tiki.vn/tam-the-3-tu-than-song-mai-p92859060.html?spid=108931251')
        book = x.build_book()
        print(book)
