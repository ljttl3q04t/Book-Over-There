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
    number_phone = models.CharField(max_length=200, null=True, blank=True)
    email = models.EmailField(max_length=100, unique=True)
    location = models.CharField(max_length=200, null=True, blank=True)


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

    def __str__(self):
        return self.name


class BookCopy(BaseModel):
    NEW = 'new'
    USED = 'used'
    LOST = 'lost'
    RETURN = 'return'
    BORROWED = 'borrowed'

    BOOK_STATUS_CHOICE = (
        (NEW, 'New'),
        (USED, 'Used'),
        (LOST, 'Lost'),
        (RETURN, 'Return'),
        (BORROWED, 'Borrowed'),
    )
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book_status = models.CharField(max_length=20, choices=BOOK_STATUS_CHOICE, default=NEW)
    book_deposit_price = models.IntegerField(default=None)
    book_deposit_status = models.IntegerField(default=None)


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
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Member(BaseModel):
    ACTIVE = 'active'
    BANNED = 'banned'
    MEMBER_STATUS_CHOICES = (
        (ACTIVE, 'Active'),
        (BANNED, 'Banned'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book_clubs = models.ManyToManyField(BookClub, through='Membership')
    member_status = models.CharField(max_length=10, choices=MEMBER_STATUS_CHOICES, default=ACTIVE)

    def __str__(self):
        return f"{self.user.username}"


class Membership(BaseModel):
    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    book_club = models.ForeignKey(BookClub, on_delete=models.CASCADE)
    joined_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.member.user.username} - {self.book_club.name}"

