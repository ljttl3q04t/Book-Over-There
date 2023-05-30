from django import forms
from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission


class User(AbstractUser):
    # Add related_name arguments to avoid clashes with auth.User model
    groups = models.ManyToManyField(Group, related_name='service_users')
    user_permissions = models.ManyToManyField(Permission, related_name='service_users')
    number_phone = models.CharField(max_length=200)
    location = models.CharField(max_length=200)


class Category(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class Author(models.Model):
    name = models.CharField(max_length=200)


class Publisher(models.Model):
    name = models.CharField(max_length=200)


class Book(models.Model):
    name = models.CharField(max_length=200)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    image = models.CharField(max_length=200)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    publisher = models.ForeignKey(Publisher, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class BookCopy(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book_status = models.IntegerField()
    book_deposit_price = models.IntegerField(default=None)
    book_deposit_status = models.IntegerField(default=None)


class Borrowing(models.Model):
    borrower_user = models.ForeignKey(User, on_delete=models.CASCADE)
    borrowing_date = models.DateTimeField()
    comment = models.CharField(max_length=200, default=None)
    status = models.IntegerField()


class BorrowingDetail(models.Model):
    borrowing = models.ForeignKey(Borrowing, on_delete=models.CASCADE)
    book_copy = models.ForeignKey(BookCopy, on_delete=models.CASCADE)
    due_date = models.DateTimeField()
    return_date = models.DateTimeField()
    deposit_status = models.IntegerField()


class WishList(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)

