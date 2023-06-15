from django.contrib import admin

from .models import Book, BookCopy, Publisher, Category, User, Author, BookClub, Membership, Member, Permission

admin.site.register(Permission)
admin.site.register(Book)
admin.site.register(BookCopy)
admin.site.register(Publisher)
admin.site.register(Category)
admin.site.register(User)
admin.site.register(Author)
admin.site.register(BookClub)
admin.site.register(Membership)
admin.site.register(Member)
