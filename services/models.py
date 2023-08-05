from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models
from django.db.models import QuerySet
from django.db.models.manager import BaseManager

from services import utils
from services.storage_backends import UserAvatarStorage, BaseStaticStorage, BookCoverStorage

class BookQuerySet(QuerySet):
    def __init__(self, *args, **kwargs):
        super(BookQuerySet, self).__init__(*args, **kwargs)

    def pk_list(self):
        return list(self.values_list("pk", flat=True))

    def flat_list(self, field, distinct=False):
        qs = self.values_list(field, flat=True)
        qs = qs.distinct() if distinct else qs
        return list(qs)

    def filter_ignore_none(self, *args, **kwargs):
        not_none_kwargs = utils.remove_none_value_in_dict(kwargs)
        return self.filter(*args, **not_none_kwargs)

    def exclude_ignore_none(self, *args, **kwargs):
        not_none_kwargs = utils.remove_none_value_in_dict(kwargs)
        return self.exclude(*args, **not_none_kwargs)

class Manager(BaseManager.from_queryset(BookQuerySet)):
    pass

class BaseModel(models.Model):
    objects = Manager()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def as_dict(self, fields=None, exclude=None):
        opts = self._meta
        data = {}
        fs = list(opts.concrete_fields) + list(opts.many_to_many)
        for f in fs:
            if fields and f.name not in fields:
                continue
            if exclude and f.name in exclude:
                continue
            else:
                data[f.name] = f.value_from_object(self)
        return data

    class Meta:
        abstract = True

class UploadFile(BaseModel):
    uploaded_at = models.DateTimeField(auto_now_add=True)
    file = models.FileField(storage=BaseStaticStorage())

    def __str__(self):
        return self.file.name

class User(AbstractUser, BaseModel):
    # Add related_name arguments to avoid clashes with auth.User model
    groups = models.ManyToManyField(Group, related_name='service_users')
    user_permissions = models.ManyToManyField(Permission, related_name='service_users')
    phone_number = models.CharField(max_length=200, null=True, unique=True)
    email = models.EmailField(max_length=100, unique=True)
    address = models.CharField(max_length=200, null=True, blank=True)
    full_name = models.CharField(max_length=200, null=True, blank=True)
    birth_date = models.DateField(null=True)
    avatar = models.FileField(storage=UserAvatarStorage(), default=None, blank=True, null=True)
    is_verify = models.BooleanField(default=False)

class OTP(BaseModel):
    OTP_CODE_LENGTH = 6
    OTP_EXPIRY_LENGTH = 5  # minutes

    phone_number = models.CharField(max_length=15)
    otp_code = models.CharField(max_length=OTP_CODE_LENGTH)
    expiry_date = models.DateTimeField()
    message_sid = models.CharField(max_length=50, null=True, blank=True)
    enable = models.BooleanField(default=True)

    class Meta:
        db_table = 'services_otp'
        index_together = ['phone_number', 'enable']

class Category(BaseModel):
    name = models.CharField(max_length=200, unique=True)
    follower = models.CharField(max_length=20, null=True, blank=True)

    def __str__(self):
        return self.name

class Author(BaseModel):
    name = models.CharField(max_length=200, unique=True)

    def __str__(self):
        return self.name

class Publisher(BaseModel):
    name = models.CharField(max_length=200, unique=True)

    def __str__(self):
        return self.name

class Book(BaseModel):
    name = models.CharField(max_length=200, db_index=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, blank=True, null=True)
    image = models.FileField(storage=BookCoverStorage(), default=None, blank=True, null=True)
    author = models.ForeignKey(Author, on_delete=models.CASCADE, blank=True, null=True)
    publisher = models.ForeignKey(Publisher, on_delete=models.CASCADE, default=None, blank=True, null=True)
    description = models.TextField(null=True)

    def __str__(self):
        return self.name

class BookCopy(BaseModel):
    NEW = 'new'
    USED = 'used'
    LOST = 'lost'
    RETURN = 'return'
    BORROWED = 'borrowed'
    SHARING_CLUB = 'sharing_club'

    BOOK_STATUS_CHOICES = (
        (NEW, 'New'),
        (USED, 'Used'),
        (LOST, 'Lost'),
        (RETURN, 'Return'),
        (BORROWED, 'Borrowed'),
        (SHARING_CLUB, 'Sharing Club')
    )
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=10, db_index=True, null=True, blank=True)
    book_status = models.CharField(max_length=20, choices=BOOK_STATUS_CHOICES, default=NEW)

    def __str__(self):
        return f'{self.user.username} - {self.book.name}'

class BookClub(BaseModel):
    name = models.CharField(max_length=100)
    description = models.TextField()
    details = models.JSONField(default=dict)
    address = models.TextField(default='', null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    code = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return f'{self.id} - {self.name}'

class Member(BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    book_clubs = models.ManyToManyField(BookClub, through='Membership')
    full_name = models.CharField(max_length=200)
    birth_date = models.DateField(null=True, blank=True)
    email = models.EmailField(max_length=100, null=True, blank=True)
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    address = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self):
        return f"{self.id} - {self.full_name}"

    def as_dict(self, fields=None, exclude=None):
        res = BaseModel.as_dict(self, exclude=['book_clubs'])
        return res

class Membership(BaseModel):
    PENDING = 'pending'
    ACTIVE = 'active'
    BANNED = 'banned'
    MEMBER_STATUS_CHOICES = (
        (PENDING, 'Pending'),
        (ACTIVE, 'Active'),
        (BANNED, 'Banned'),
    )
    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    book_club = models.ForeignKey(BookClub, on_delete=models.CASCADE)
    member_status = models.CharField(max_length=10, choices=MEMBER_STATUS_CHOICES, default=PENDING)
    joined_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    leaved_at = models.DateField(null=True, default=None, blank=True)
    is_staff = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.id} - {self.member.full_name} - {self.book_club.name}"

class MemberBookCopy(BaseModel):
    membership = models.ForeignKey(Membership, on_delete=models.CASCADE)
    book_copy = models.ForeignKey(BookCopy, on_delete=models.CASCADE)
    date_added = models.DateField(auto_now_add=True)
    current_reader = models.ForeignKey(Membership, on_delete=models.SET_NULL, null=True, blank=True,
                                       related_name='current_reader')
    onboard_date = models.DateField(null=True, blank=True)
    is_enabled = models.BooleanField(default=True)

    def __str__(self):
        return f'{self.id} - {self.membership.member.full_name} - {self.book_copy.book.name}'

# Draft -> Created, Cancelled
# Created -> Cancelled, Confirmed
# Created -> Confirmed: start borrowing
# Confirmed -> Overdue: out of due_date
# Confirmed -> Completed
# Overdue -> Completed
class MembershipOrder(BaseModel):
    DRAFT = 'draft'
    CANCEL = 'Cancel'
    CREATED = 'Created'
    CONFIRMED = 'Confirmed'
    OVERDUE = 'Overdue'
    COMPLETED = 'Completed'

    MEMBERSHIP_ORDER_STATUS_CHOICE = (
        (DRAFT, 'Draft'),
        (CANCEL, 'Cancel'),
        (CREATED, 'Created'),
        (CONFIRMED, 'Confirmed'),
        (OVERDUE, 'Overdue'),
        (COMPLETED, 'Completed'),
    )

    membership = models.ForeignKey(Membership, on_delete=models.CASCADE)
    order_date = models.DateField(auto_created=True, auto_now_add=True)
    confirm_date = models.DateField(null=True)
    order_status = models.CharField(max_length=20, choices=MEMBERSHIP_ORDER_STATUS_CHOICE, default=CREATED)

    def __str__(self):
        return f'{self.id} - {self.membership}'

class MembershipOrderDetail(BaseModel):
    order = models.ForeignKey(MembershipOrder, on_delete=models.CASCADE, related_name='membership_order_details')
    member_book_copy = models.ForeignKey(MemberBookCopy, on_delete=models.CASCADE)
    due_date = models.DateTimeField()
    return_date = models.DateTimeField(null=True, blank=True)
    overdue_day_count = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f'{self.id} - orderId: {self.order.id} - {self.member_book_copy}'

class BookCopyHistory(BaseModel):
    DONATE_TO_CLUB = "donate_to_club"
    WITHDRAW_BOOK_FROM_CLUB = "withdraw_book_from_club"
    CLUB_BORROW_BOOK = 'club_borrow_book'
    CLUB_EXTEND_DUE_DATE = 'club_extend_due_date'
    CLUB_RETURN_BOOK = 'club_return_book'

    ACTION_CHOICES = (
        (DONATE_TO_CLUB, 'donate_to_club'),
        (WITHDRAW_BOOK_FROM_CLUB, "withdraw_book_from_club"),
        (CLUB_BORROW_BOOK, 'club_borrow_book'),
        (CLUB_EXTEND_DUE_DATE, 'club_extend_due_date'),
        (CLUB_RETURN_BOOK, 'club_return_book'),
    )

    book_copy = models.ForeignKey(BookCopy, on_delete=models.CASCADE)
    action = models.CharField(max_length=50, choices=ACTION_CHOICES, default=DONATE_TO_CLUB)
    membership_borrower = models.ForeignKey(Membership, on_delete=models.CASCADE, null=True, blank=True)
    description = models.TextField(blank=True)
    attachment = models.ForeignKey(UploadFile, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"{self.book_copy} - {self.action}"
