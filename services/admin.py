from django.contrib import admin

from .models import Question
from .models import Book

admin.site.register(Question)
admin.site.register(Book)
