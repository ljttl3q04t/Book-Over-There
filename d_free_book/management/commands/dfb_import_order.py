import csv
from datetime import timedelta, datetime

from django.core.management import BaseCommand
from django.db import transaction

from d_free_book.models import DFreeMember, ClubBook, DFreeOrder, DFreeOrderDetail
from services.models import BookClub

NO_CODE = ['K mã', 'K khớp mã trên link', 'K mã ', 'Ko mã ', 'k mã', 'k có mã', 'ko mã', 'Ko mã']
ERROR_ORDERS = ['2301_1_1', '2301_1_2', '2301_2_2', '2301_6_1', '2301_8_2', '2301_9_3', '2301_11_3', '2301_12_1',
                '2301_13_1', '2301_13_4', '2301_13_4', '2301_15_1', '2301_15_1', '2301_15_1', '2301_15_1', '2301_31_3',
                '2301_31_4', '2302_2_4', '2302_3_2', '2302_5_2', '2302_6_6', '2302_7_7', '2302_8_2', '2302_9_3',
                '2302_11_4', '2302_12_5', '2302_17_3', '2302_17_6', '2302_17_9', '2302_18_3', '2302_18_12',
                '2302_18_12', '2302_18_12', '2302_18_12', '2302_19_6', '2302_19_6', '2302_28_1', '2303_4_5', '2303_6_1',
                '2303_6_3', '2303_8_1', '2303_8_4', '2303_8_4', '2303_12_6', '2303_12_9', '2303_15_9', '2303_18_8',
                '2303_19_8', '2303_23_4', '2303_30_3', '2303_31_1', '2303_31_1', '2303_31_2', '2303_31_3', '2304_1_1',
                '2304_1_3', '2304_3_5', '2304_3_7', '2304_5_2', '2304_5_2', '2304_7_8', '2304_7_8', '2304_7_8',
                '2304_7_8', '2304_7_8', '2304_9_3', '2304_9_4', '2304_10_3', '2304_11_5', '2304_11_9', '2304_11_9',
                '2304_11_9', '2304_11_9', '2304_11_9', '2304_16_3', '2304_16_5', '2304_16_5', '2304_16_5', '2304_16_5',
                '2304_20_1', '2304_20_7', '2304_21_3', '2304_21_3', '2304_21_4', '2304_21_4', '2304_22_1', '2304_22_1',
                '2304_22_1', '2304_22_1', '2304_24_4', '2304_24_8', '2304_24_8', '2304_24_8', '2304_24_8', '2304_24_8',
                '2304_26_1', '2304_27_3', '2304_27_7', '2304_27_8', '2304_27_8', '2304_27_8', '2304_27_10',
                '2304_27_10', '2304_28_8', '2305_2_1', '2305_3_2', '2305_3_2', '2305_3_2', '2305_4_6', '2305_4_7',
                '2305_7_3', '2305_7_3', '2305_7_3', '2305_7_3', '2305_7_3', '2305_8_2', '2305_8_2', '2305_10_1',
                '2305_10_6', '2305_11_1', '2305_11_2', '2305_13_9', '2305_13_9', '2305_15_2', '2305_16_2', '2305_16_5',
                '2305_16_6', '2305_16_7', '2305_16_7', '2305_16_7', '2305_17_3', '2305_20_5', '2305_20_5', '2305_20_5',
                '2305_21_2', '2305_22_1', '2305_22_5', '2305_22_5', '2305_22_5', '2305_24_3', '2305_26_2', '2305_26_2',
                '2305_29_10', '2305_30_1', '2305_30_1', '2305_30_1', '2305_30_1', '2305_30_1', '2305_31_3', '2306_4_2',
                '2306_5_1', '2306_7_4', '2306_9_1', '2306_10_3', '2306_11_1', '2306_11_1', '2306_11_6', '2306_13_1',
                '2306_13_2', '2306_16_2', '2306_16_2', '2306_16_3', '2306_16_3', '2306_23_7', '2306_23_7', '2306_26_5',
                '2306_27_4', '2306_27_5', '2306_27_7', '2306_28_2', '2307_1_4', '2307_6_1', '2307_9_1', '2307_9_2',
                '2307_12_4']

MAP_ORDER_STATUS = {
    'Đang mượn': DFreeOrderDetail.CREATED,
    'Đã trả': DFreeOrderDetail.COMPLETE,
    'Quá hạn': DFreeOrderDetail.OVERDUE,
}

class ImportException(Exception):
    def __init__(self, fcode, row, cause):
        self.fcode = fcode
        self.row = row
        self.cause = cause
        super().__init__()

def convert_to_date(year, month, day):
    date_string = f"{year}-{month}-{day}"
    date = datetime.strptime(date_string, "%Y-%m-%d").date()
    return date

def convert_return_date(date_string, default_year=2023):
    if '/' in date_string and len(date_string.split('/')) == 3:
        date_string = '/'.join(date_string.split('/')[:-1])

    if '/' in date_string and len(date_string.split('/')) == 2:
        date_string = date_string + '/' + str(default_year)

    try:
        date = datetime.strptime(date_string, '%d/%m/%Y').date()
        return date
    except ValueError:
        raise ValueError("Invalid_date={}".format(date_string))

def verify_row(row, fcode):
    if len(row) == 16:
        day_index, order_index, book_name, book_code, full_name, phone_number, member_code, note, order_status, return_date, days, overdue_days, fee, note2, _, _ = row
    elif len(row) == 17:
        day_index, order_index, book_name, book_code, full_name, phone_number, member_code, note, order_status, return_date, days, overdue_days, fee, note2, _, _, _ = row
    else:
        raise ImportException(fcode, row, "check_length")

    if not member_code or not full_name:
        raise ImportException(fcode, row, 'check_member_code')

    if not book_code:
        raise ImportException(fcode, row, 'check_book_code')

    if order_status not in ['Đang mượn', 'Đã trả', 'Quá hạn']:
        raise ImportException(fcode, row, 'check_order_status')
    order_status = MAP_ORDER_STATUS[order_status]

    try:
        order_date = convert_to_date('2023', fcode[-2:], day_index)
        due_date = order_date + timedelta(days=35)
    except:
        raise ImportException(fcode, row, 'check_order_date')

    try:
        if return_date.startswith("?"):
            return_date = None
        elif return_date:
            return_date = convert_return_date(return_date)
        else:
            return_date = None
    except:
        raise ImportException(fcode, row, 'check_return_date')

    book_note = None
    club_book = None
    if book_code in NO_CODE:
        book_note = book_name
    else:
        club_book = ClubBook.objects.filter(code=book_code).first()
        if not club_book:
            raise ImportException(fcode, row, 'book_not_found')

    if not book_note and not club_book:
        raise ImportException(fcode, row, 'check_book')

    note = note if note else note2 if note2 else None

    return {
        'day_index': day_index,
        'order_index': order_index,
        'book_name': book_name,
        'book_code': book_code,
        'full_name': full_name,
        'phone_number': phone_number,
        'member_code': member_code,
        'note': note,
        'order_status': order_status,
        'return_date': return_date,
        'days': days,
        'overdue_days': overdue_days,
        'fee': fee,
        'club_book': club_book,
        'book_note': book_note,
        'order_date': order_date,
        'due_date': due_date,
    }

@transaction.atomic
def import_order_from_csv(file_path, fcode, club_id):
    with open(file_path, 'r') as csv_file:
        reader = csv.reader(csv_file)
        next(reader)
        next(reader)

        today = datetime.now().date()
        new_order = None
        current_order = None
        error_orders = []
        success_rows = 0
        for row in reader:
            order_code = "{}_{}_{}".format(fcode, row[0], row[1])
            try:
                data = verify_row(row, fcode)
            except ImportException as e:
                # print("error|{}|{}|{}".format(order_code, e.cause, e.row))
                error_orders.append("{}_{}_{}".format(fcode, row[0], row[1]))
                continue

            if order_code in ERROR_ORDERS:
                # print("error|{}|{}|{}".format(order_code, "check_order_detail", row))
                continue

            dfb_member, _ = DFreeMember.objects.get_or_create(code=data['member_code'], full_name=data['full_name'])
            if data['order_index'] != new_order:
                new_order = data['order_index']
                current_order = DFreeOrder.objects.create(
                    club_id=club_id,
                    member=dfb_member,
                    order_date=data['order_date'],
                    due_date=data['due_date'],
                )
            order_status = data['order_status']
            overdue_day_count = 0
            if order_status == DFreeOrderDetail.COMPLETE:
                if data['return_date']:
                    overdue_day_count = max((data['return_date'] - current_order.due_date).days, 0)
            else:
                overdue_day_count = max((today - current_order.due_date).days, 0)
                if overdue_day_count:
                    order_status = DFreeOrderDetail.OVERDUE

            if data['club_book']:
                DFreeOrderDetail.objects.create(
                    order=current_order,
                    club_book=data['club_book'],
                    return_date=data['return_date'],
                    note=data['note'],
                    order_status=order_status,
                    overdue_day_count=overdue_day_count,
                )
            else:
                DFreeOrderDetail.objects.create(
                    order=current_order,
                    book_note=data['book_note'],
                    return_date=data['return_date'],
                    note=data['note'],
                    order_status=order_status,
                    overdue_day_count=overdue_day_count,
                )
            success_rows += 1

        print("{}|success_row|{}".format(fcode, success_rows))
        return error_orders

class Command(BaseCommand):
    help = "import order for d free book"

    def handle(self, *args, **options):
        file_names = ['2301', '2302', '2303', '2304', '2305', '2306', '2307']
        error_orders = []
        club_id = BookClub.objects.get(code='dfb_caugiay').id

        for fn in file_names:
            file_path = '/home/tintin/Downloads/' + fn + '.csv'
            try:
                error_orders = error_orders + import_order_from_csv(file_path, fn, club_id)
            except Exception as e:
                print("error|{}|{}".format(fn, e))

        # print(error_orders)
        # print(len(error_orders))

# day    order book_name             b_code    member_full_name      phone_number  m_code     note   order_status   return    days   overdue    fee     note2    _    _
# ['24', '6',  'Conan tập 92',         'K mã ', 'Nguyễn Phương Linh', '0944621810', 'LinhNP',   '', '  Đã trả',      '27/06',  '',    '',        '',     '',      '5', '']
# ['8',  '6',  'Phía sau nghi can X',  'E5-01', 'Nguyễn Ngọc Lan',    '0339101176', 'LanNN',    '',   'Quá hạn',     '',       '37',  '2',       '2000', '',      '3', '']
# ['14', '3',  'Tình sinh ý động 2',   'B6-26', 'Nguyễn Như Phúc',    '0813312536', 'PhucNN',   '',   'Đang mượn',   '',       '31',  '',        '',     '',      '2', '']
# ['1',  '1',  'Tư tưởng Phật học',    'C1-36', 'Nông Thị Hoa',       '0818501527', 'HoaNT1',   '',   'Đã trả',      '2/3',    '',    '',        '',     '',      '1', '', '']
