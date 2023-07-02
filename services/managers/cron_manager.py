from datetime import date

from django.db import transaction

from services.models import MembershipOrder, MembershipOrderDetail
import logging

@transaction.atomic
def evaluate_overdue_day():
    log = logging.getLogger('django')
    log.info('started|evaluate_overdue_day')
    today = date.today()
    working_orders = MembershipOrder.objects.filter(order_status__in=[MembershipOrder.CONFIRMED, MembershipOrder.OVERDUE])
    order_details = MembershipOrderDetail.objects.filter(order__in=working_orders)
    for order_detail in order_details:
        time_delta = today - order_detail.due_date.date()
        if time_delta.days > 0:
            order_detail.overdue_day_count = time_delta.days
            order_detail.order.order_status = MembershipOrder.OVERDUE
            order_detail.save()

    log.info('finished|evaluate_overdue_day')
