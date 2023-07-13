from django.db import transaction

from d_free_book.models import ClubBook, DFreeOrder, DFreeMember, DFreeOrderDetail
from services.managers.book_manager import get_book_infos, create_book
from services.managers.cache_manager import combine_key_cache_data, CACHE_KEY_CLUB_BOOK_INFOS, \
    CACHE_KEY_DFB_ORDER_INFOS, CACHE_KEY_MEMBER_INFOS

def get_club_book_records(club_book_ids=None, club_id=None, book_ids=None):
    return ClubBook.objects.filter_ignore_none(
        id__in=club_book_ids,
        club_id=club_id,
        book_id__in=book_ids,
    )

def get_member_records(phone_number=None, code=None, member_ids=None):
    return DFreeMember.objects.filter_ignore_none(
        id__in=member_ids,
        phone_number=phone_number,
        code=code,
    )

@combine_key_cache_data(**CACHE_KEY_MEMBER_INFOS)
def get_member_infos(member_ids):
    members = get_member_records(member_ids=member_ids)
    result = {}
    for member in members:
        result[member.id] = {
            'phone_number': member.phone_number,
            'full_name': member.full_name,
            'code': member.code,
        }
    return result

def get_order_records(order_ids=None, club_id=None, member_ids=None, from_date=None, to_date=None, order_status=None):
    return DFreeOrder.objects.filter_ignore_none(
        id__in=order_ids,
        club_id=club_id,
        member_id__in=member_ids,
        order_date__gte=from_date,
        order_date__lte=to_date,
        order_status=order_status,
    )

def get_order_detail_records(order_ids=None, order_detail_ids=None):
    return DFreeOrderDetail.objects.filter_ignore_none(
        id__in=order_detail_ids,
        order_id__in=order_ids
    )

@combine_key_cache_data(**CACHE_KEY_CLUB_BOOK_INFOS)
def get_club_book_infos(club_book_ids):
    if not club_book_ids:
        return {}
    club_books = get_club_book_records(club_book_ids=club_book_ids)
    book_ids = [b.book_id for b in club_books]
    book_infos = get_book_infos(book_ids)
    result = {}
    for club_book in club_books:
        result[club_book.id] = {
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

    result = {}
    for order_detail in order_details:
        club_book_info = club_book_infos.get(order_detail.club_book_id)
        result[order_detail.id] = {
            'book_code': club_book_info['code'] if club_book_info else None,
            'book_name': club_book_info['book']['name'] if club_book_info else None,
            'order_id': order_detail.order_id,
            'return_date': order_detail.return_date,
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

    result = {}
    for order in orders:
        order_details = map_order_order_details.get(order.id)
        result[order.id] = {
            'id': order.id,
            'member': member_infos.get(order.member_id),
            'club_id': order.club_id,
            'order_date': order.order_date,
            'due_date': order.due_date,
            'order_status': order.order_status,
            'order_details': order_details
        }

    return result

@transaction.atomic
def create_club_book(data):
    book = create_book(
        name=data['name'],
        category=data['category'],
        author=data['author'],
        image=data['image'],
    )
    ClubBook.objects.create(
        book=book,
        code=data['code'],
        club_id=data['club_id'],
        init_count=data['init_count'],
        current_count=data['current_count'],
    )
