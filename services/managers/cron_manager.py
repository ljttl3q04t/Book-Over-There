from datetime import date

from django.db import transaction
from django.db.models import Q

from d_free_book.models import DFreeOrder, DFreeOrderDetail
from services.managers.email_manager import send_overdue_notification_email
from services.models import MembershipOrder, MembershipOrderDetail
import logging

log = logging.getLogger('django')

@transaction.atomic
def cron_evaluate_overdue_day():
    log.info('started|cron_evaluate_overdue_day')
    today = date.today()
    working_orders = DFreeOrder.objects.filter(Q(order_date__lte=today) & Q(due_date__gte=today))
    order_details = DFreeOrderDetail.objects.filter(order__in=working_orders)
    for order_detail in order_details:
        time_delta = order_detail.order.due_date - today
        if time_delta.days >= 0:
            order_detail.overdue_day_count = time_delta.days + 1
            order_detail.order_status = DFreeOrderDetail.CREATED
        order_detail.save()
    finish_oder = DFreeOrder.objects.filter(Q(due_date__lt=today))
    order_detail_over_due = DFreeOrderDetail.objects.filter(order__in=finish_oder, order_status__in=DFreeOrderDetail.CREATED)
    for order_detail in order_detail_over_due:
        time_delta = order_detail.order.due_date - today
        if time_delta.days < 0:
            order_detail.order_status = DFreeOrderDetail.OVERDUE
            order_detail.overdue_day_count = None
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
