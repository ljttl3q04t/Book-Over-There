from django.shortcuts import render
from rest_framework.pagination import PageNumberPagination
from rest_framework import generics
from .models import Book
from .serializers import BookSerializer

class CustomPagination(PageNumberPagination):
    page_size = 10  # Set the desired page size
    page_size_query_param = 'page_size'  # Customize the query parameter for specifying the page size
    max_page_size = 100  # Set the maximum allowed page size


class BookListAPIView(generics.ListAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    pagination_class = CustomPagination

def index(request):
    return render(request, "services/index.html")

def viewListBook(request):
    list_book = Book.objects.all()
    context = {"listBooks": list_book}
    return render(request, "services/book_list.html", context)
