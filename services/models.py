from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class User(AbstractUser, BaseModel):
    # Add related_name arguments to avoid clashes with auth.User model
    groups = models.ManyToManyField(Group, related_name='service_users')
    user_permissions = models.ManyToManyField(Permission, related_name='service_users')
    phone_number = models.CharField(max_length=200, null=True, blank=True)
    email = models.EmailField(max_length=100, unique=True)
    address = models.CharField(max_length=200, null=True, blank=True)
    full_name = models.CharField(max_length=200, null=True, blank=True)
    birth_date = models.DateField(null=True)
    user_card_photo = models.ImageField(upload_to='images', null=False, default=None)

class Category(BaseModel):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class Author(BaseModel):
    name = models.CharField(max_length=200)


class Publisher(BaseModel):
    name = models.CharField(max_length=200)


class Book(BaseModel):
    name = models.CharField(max_length=200, db_index=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    image = models.CharField(max_length=200)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    publisher = models.ForeignKey(Publisher, on_delete=models.CASCADE)
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
    book_status = models.CharField(max_length=20, choices=BOOK_STATUS_CHOICES, default=NEW)
    book_deposit_price = models.IntegerField(null=True, default=None, blank=True)
    book_deposit_status = models.IntegerField(null=True, default=None, blank=True)
    book_image = models.ImageField(upload_to='images', null=False, default=None)

    def __str__(self):
        return f'{self.user.username} - {self.book.name} -{self.book_image}'

class Order(BaseModel):
    order_user = models.ForeignKey(User, on_delete=models.CASCADE)
    order_date = models.DateTimeField()
    total_book = models.IntegerField()
    comment = models.CharField(max_length=200, default=None)
    status = models.IntegerField()


class OrderDetail(BaseModel):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_details')
    book_copy = models.ForeignKey(BookCopy, on_delete=models.CASCADE)
    due_date = models.DateTimeField()
    return_date = models.DateTimeField()


class WishList(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)


class BookClub(BaseModel):
    name = models.CharField(max_length=100)
    description = models.TextField()
    address = models.TextField(default='', null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Member(BaseModel):
    PENDING = 'pending'
    ACTIVE = 'active'
    BANNED = 'banned'
    MEMBER_STATUS_CHOICES = (
        (PENDING, 'Pending'),
        (ACTIVE, 'Active'),
        (BANNED, 'Banned'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book_clubs = models.ManyToManyField(BookClub, through='Membership')
    member_status = models.CharField(max_length=10, choices=MEMBER_STATUS_CHOICES, default=PENDING)
    full_name = models.CharField(max_length=200)
    birth_date = models.DateField()
    email = models.EmailField(max_length=100)
    phone_number = models.CharField(max_length=20)
    address = models.CharField(max_length=200)

    # student_card = models.CharField(max_length=200)

    def __str__(self):
        return f"{self.full_name}"


class Membership(BaseModel):
    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    book_club = models.ForeignKey(BookClub, on_delete=models.CASCADE)
    joined_at = models.DateTimeField(auto_now_add=True)
    leaved_at = models.DateField(null=True, default=None, blank=True)

    def __str__(self):
        return f"{self.member.full_name} - {self.book_club.name}"


class MemberBookCopy(BaseModel):
    NEW = 'new'
    USED = 'used'
    LOST = 'lost'
    RETURN = 'return'
    BORROWED = 'borrowed'

    BOOK_STATUS_CHOICES = (
        (NEW, 'New'),
        (USED, 'Used'),
        (LOST, 'Lost'),
        (RETURN, 'Return'),
        (BORROWED, 'Borrowed'),
    )
    membership = models.ForeignKey(Membership, on_delete=models.CASCADE)
    book_copy = models.ForeignKey(BookCopy, on_delete=models.CASCADE)
    date_added = models.DateField(auto_now_add=True)
    book_status = models.CharField(max_length=20, choices=BOOK_STATUS_CHOICES, default=NEW)
    current_reader = models.ForeignKey(Membership, on_delete=models.SET_NULL, null=True, blank=True,
                                       related_name='current_reader')

    def __str__(self):
        return f'{self.membership.member.full_name} - {self.book_copy.book.name}'


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
    order_date = models.DateField(auto_created=True)
    confirm_date = models.DateField(null=True)
    order_status = models.CharField(max_length=20, choices=MEMBERSHIP_ORDER_STATUS_CHOICE, default=CREATED)


class MembershipOrderDetail(BaseModel):
    order = models.ForeignKey(MembershipOrder, on_delete=models.CASCADE, related_name='membership_order_details')
    member_book_copy = models.ForeignKey(MemberBookCopy, on_delete=models.CASCADE)
    due_date = models.DateTimeField()
    return_date = models.DateTimeField(null=True)
    overdue_day_count = models.IntegerField(null=True)

# TODO: BookLost
