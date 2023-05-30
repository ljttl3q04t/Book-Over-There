from django.contrib import admin

from .models import Book, BookCopy, BorrowingDetail, Borrowing, Publisher, Category, User, Author

admin.site.register(Book)
admin.site.register(BookCopy)
admin.site.register(BorrowingDetail)
admin.site.register(Borrowing)
admin.site.register(Publisher)
admin.site.register(Category)
admin.site.register(User)
admin.site.register(Author)

