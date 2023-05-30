from django.http import HttpResponse
from django.shortcuts import render
from .models import Book
from rest_framework import views


def index(request):
    return render(request, "services/index.html")


def viewListBook(request):
    list_book = Book.objects.all()
    context = {"listBooks": list_book}
    return render(request, "services/book_list.html", context)
