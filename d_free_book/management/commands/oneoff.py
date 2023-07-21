from django.core.management import BaseCommand

from services.managers.cron_manager import cron_evaluate_overdue_day

class Command(BaseCommand):
    def handle(self, *args, **options):
        # cron_evaluate_overdue_day()
        print("hehe")
