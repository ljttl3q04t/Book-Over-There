from django.db import transaction

from d_free_book.models import ClubBook, DFreeOrder, DFreeMember, DFreeOrderDetail
from services.managers import membership_manager, book_manager
from services.managers.cache_manager import combine_key_cache_data, CACHE_KEY_CLUB_BOOK_INFOS, \
    CACHE_KEY_DFB_ORDER_INFOS, CACHE_KEY_MEMBER_INFOS, invalid_cache_data

def get_club_book_records(club_book_ids=None, club_id=None, book_ids=None, code=None, club_ids=None):
    return ClubBook.objects.filter_ignore_none(
        id__in=club_book_ids,
        club_id=club_id,
        club_id__in=club_ids,
        book_id__in=book_ids,
        code=code,
    )

def get_member_records(phone_number=None, code=None, member_ids=None, full_name=None, club_ids=None):
    return DFreeMember.objects.filter_ignore_none(
        id__in=member_ids,
        club_id__in=club_ids,
        phone_number=phone_number,
        code=code,
        full_name=full_name,
    )

def create_member(club_id, full_name, code, phone_number=None):
    return DFreeMember.objects.create(
        club_id=club_id,
        full_name=full_name,
        code=code,
        phone_number=phone_number
    )

def update_member(member_id, club_ids, **kwargs):
    affected_count = DFreeMember.objects.filter(id=member_id, club_id__in=club_ids).update(**kwargs)
    if affected_count:
        cache_key = CACHE_KEY_MEMBER_INFOS['cache_key_converter'](CACHE_KEY_MEMBER_INFOS['cache_prefix'], member_id)
        invalid_cache_data(cache_key)

    return affected_count

@combine_key_cache_data(**CACHE_KEY_MEMBER_INFOS)
def get_member_infos(member_ids):
    members = get_member_records(member_ids=member_ids)
    result = {}
    for member in members:
        result[member.id] = {
            'id': member.id,
            'club_id': member.club_id,
            'phone_number': member.phone_number,
            'full_name': member.full_name,
            'code': member.code,
        }
    return result

def get_order_records(order_ids=None, club_id=None, member_ids=None, from_date=None, to_date=None, club_ids=None, order_date=None):
    return DFreeOrder.objects.filter_ignore_none(
        id__in=order_ids,
        club_id=club_id,
        club_id__in=club_ids,
        member_id__in=member_ids,
        order_date__gte=from_date,
        order_date__lte=to_date,
        order_date=order_date,
    )

def get_order_detail_records(order_ids=None, order_detail_ids=None, order_status=None, receiver_book=None):
    return DFreeOrderDetail.objects.filter_ignore_none(
        id__in=order_detail_ids,
        order_id__in=order_ids,
        order_status=order_status,
        receiver_book=receiver_book,
    )

@transaction.atomic
def create_new_order(data):
    order = DFreeOrder.objects.create(
        member_id=data.get('member_id'),
        club_id=data.get('club_id'),
        order_date=data.get('order_date'),
        due_date=data.get('due_date'),
        creator_order_id=data.get('creator_order_id'),
    )
    for club_book_id in data.get('club_book_ids'):
        DFreeOrderDetail.objects.create(
            order=order,
            club_book_id=club_book_id,
        )


@transaction.atomic
def create_new_order_by_new_member(data):
    new_member = data.get('new_member')
    new_member = DFreeMember.objects.create(
        club_id=data.get('club_id'),
        full_name=new_member.get('full_name'),
        code=new_member.get('code'),
        phone_number=new_member.get('phone_number')
    )
    order = DFreeOrder.objects.create(
        member_id=new_member.id,
        club_id=data.get('club_id'),
        order_date=data.get('order_date'),
        due_date=data.get('due_date'),
        creator_order_id=data.get('creator_order_id'),
    )
    for club_book_id in data.get('club_book_ids'):
        DFreeOrderDetail.objects.create(
            order=order,
            club_book_id=club_book_id,
        )

def return_books(order_detail_ids, return_date, receiver_id):
    return DFreeOrderDetail.objects.filter(id__in=order_detail_ids).update(return_date=return_date, order_status=DFreeOrderDetail.COMPLETE,
                                                                           receiver_id=receiver_id)

@combine_key_cache_data(**CACHE_KEY_CLUB_BOOK_INFOS)
def get_club_book_infos(club_book_ids):
    if not club_book_ids:
        return {}
    club_books = get_club_book_records(club_book_ids=club_book_ids)
    book_ids = [b.book_id for b in club_books]
    book_infos = book_manager.get_book_infos(book_ids)
    result = {}
    for club_book in club_books:
        result[club_book.id] = {
            'id': club_book.id,
            'book': book_infos.get(club_book.book_id, {}),
            'code': club_book.code,
            'club_id': club_book.club_id,
            'init_count': club_book.init_count,
            'current_count': club_book.current_count,
        }
    return result

def get_order_detail_infos(order_detail_ids):
    if not order_detail_ids:
        return {}

    order_details = list(get_order_detail_records(order_detail_ids=order_detail_ids))
    club_book_ids = list(set([o.club_book_id for o in order_details]))
    club_book_infos = get_club_book_infos(club_book_ids)
    membership_infos = membership_manager.get_membership_infos()
    result = {}
    for order_detail in order_details:
        club_book_info = club_book_infos.get(order_detail.club_book_id)
        result[order_detail.id] = {
            'id': order_detail.id,
            'book_code': club_book_info['code'] if club_book_info else None,
            'book_name': club_book_info['book']['name'] if club_book_info else None,
            'order_id': order_detail.order_id,
            'return_date': order_detail.return_date,
            'order_status': order_detail.order_status,
            'overdue_day_count': order_detail.overdue_day_count,
            'receiver': membership_infos.get(order_detail.receiver_id)
        }
    return result

@combine_key_cache_data(**CACHE_KEY_DFB_ORDER_INFOS)
def get_order_infos(order_ids):
    if not order_ids:
        return None

    orders = list(get_order_records(order_ids))
    member_ids = [o.member_id for o in orders]
    member_infos = get_member_infos(member_ids)
    order_detail_ids = get_order_detail_records(order_ids=order_ids).pk_list()
    order_detail_infos = get_order_detail_infos(order_detail_ids)
    map_order_order_details = {}
    for order_detail in order_detail_infos.values():
        if order_detail['order_id'] not in map_order_order_details:
            map_order_order_details[order_detail['order_id']] = [order_detail]
        else:
            map_order_order_details[order_detail['order_id']].append(order_detail)

    membership_infos = membership_manager.get_membership_infos()
    result = {}
    for order in orders:
        order_details = map_order_order_details.get(order.id)
        result[order.id] = {
            'id': order.id,
            'member': member_infos.get(order.member_id),
            'club_id': order.club_id,
            'order_date': order.order_date,
            'due_date': order.due_date,
            'order_details': order_details,
            'creator_order': membership_infos.get(order.creator_order_id),
        }

    return result

@transaction.atomic
def create_club_book(data, book=None):
    if not book:
        book = book_manager.create_book(
            name=data.get('name'),
            category=data.get('category'),
            author=data.get('author'),
            image=data.get('image'),
        )

    if not book.image or not book.image.name:
        if data.get('image_url'):
            book_manager.save_image_from_url(book, data.get('image_url'))
        elif data.get('image'):
            book.image = data.get('image')
            book.save()

    ClubBook.objects.create(
        book=book,
        code=data['code'],
        club_id=data['club_id'],
        init_count=data['init_count'],
        current_count=data['current_count'],
    )

def update_club_book(club_book_id, **kwargs):
    affected_count = ClubBook.objects.filter(id=club_book_id).update(**kwargs)
    return affected_count


def validate_oder(data):
    order_ids = get_order_records(member_ids=[data['member_id']], club_id=data['club_id']).pk_list()
    has_overdue_order = get_order_detail_records(order_status=DFreeOrderDetail.OVERDUE, order_ids=order_ids).exists()
    count_created_order = get_order_detail_records(order_status=DFreeOrderDetail.CREATED, order_ids=order_ids).count()
    if has_overdue_order:
        return False, 'The User is borrowing overdue'
    if count_created_order >= 3:
        return False, 'The User is borrowing {}'.format(count_created_order)

    return True, None
