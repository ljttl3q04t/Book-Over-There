import json
import logging
from datetime import date

from django.db import transaction
from django.utils import timezone

from d_free_book.models import DFreeOrder, DFreeOrderDetail
from services.managers.email_manager import send_overdue_notification_email
from services.models import MembershipOrderDetail

log = logging.getLogger('django')

@transaction.atomic
def cron_evaluate_overdue_day():
    log.info('started|cron_evaluate_overdue_day')
    today = date.today()
    current_time = timezone.now()
    map_order_due_date = {item.id: item.due_date for item in DFreeOrder.objects.all()}
    order_details = DFreeOrderDetail.objects.all()
    data = []
    for order_detail in order_details:
        order_status = order_detail.order_status
        new_status = order_status
        new_overdue_day_count = order_detail.overdue_day_count
        return_date = order_detail.return_date.date() if order_detail.return_date else None
        due_date = map_order_due_date.get(order_detail.order_id)

        if order_status == DFreeOrderDetail.CREATED:
            new_overdue_day_count = max((today - due_date).days, 0)
            new_status = DFreeOrderDetail.OVERDUE if new_overdue_day_count > 0 else order_status
        elif order_status == DFreeOrderDetail.OVERDUE:
            new_overdue_day_count = max((today - due_date).days, 0)
        elif order_status == DFreeOrderDetail.COMPLETE:
            if not return_date:
                continue
            new_overdue_day_count = max((return_date - due_date).days, 0)

        order_detail.overdue_day_count = new_overdue_day_count
        order_detail.order_status = new_status
        order_detail.updated_at = current_time
        order_detail.save()

    with open("./alo.json", "w") as outfile:
        json.dump(data, outfile)
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
