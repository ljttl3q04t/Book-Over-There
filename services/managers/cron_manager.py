from datetime import date

from django.db import transaction

from services.managers.email_manager import send_overdue_notification_email
from services.models import MembershipOrder, MembershipOrderDetail
import logging

log = logging.getLogger('django')

@transaction.atomic
def cron_evaluate_overdue_day():
    log.info('started|cron_evaluate_overdue_day')

    today = date.today()
    working_orders = MembershipOrder.objects.filter(
        order_status__in=[MembershipOrder.CONFIRMED, MembershipOrder.OVERDUE])
    order_details = MembershipOrderDetail.objects.filter(order__in=working_orders)
    for order_detail in order_details:
        time_delta = today - order_detail.due_date.date()
        if time_delta.days > 0:
            order_detail.overdue_day_count = time_delta.days
            order_detail.order.order_status = MembershipOrder.OVERDUE
            order_detail.save()

    log.info('finished|cron_evaluate_overdue_day')

def cron_send_email_noti_overdue():
    log.info('started|cron_send_email_noti_overdue')

    order_details = MembershipOrderDetail.objects.filter(overdue_day_count__gt=0)
    for order_detail in order_details:
        membership = order_detail.order.membership
        book_title = order_detail.member_book_copy.book_copy.book.name
        due_date = order_detail.due_date
        try:
            send_overdue_notification_email(membership, book_title, due_date)
            log.info(
                'done|send_overdue_notification_email|{}|{}|{}'.format(membership.member.email, book_title, due_date))
        except:
            log.info(
                'failed|send_overdue_notification_email|{}|{}|{}'.format(membership.member.email, book_title, due_date))

    log.info('finished|cron_send_email_noti_overdue')
