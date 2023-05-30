from django.shortcuts import render
from rest_framework.pagination import PageNumberPagination
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Book, User
from .serializers import BookSerializer
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from .models import Borrowing

class CustomPagination(PageNumberPagination):
    page_size = 10  # Set the desired page size
    page_size_query_param = 'page_size'  # Customize the query parameter for specifying the page size
    max_page_size = 100  # Set the maximum allowed page size


class BookListAPIView(generics.ListAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    pagination_class = CustomPagination


class BookUpdateAPIView(APIView):
    def post(self, request, book_id):
        try:
            book = Book.objects.get(pk=book_id)
        except Book.DoesNotExist:
            return Response({"error": "Book not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = BookSerializer(book, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def index(request):
    return render(request, "services/index.html")


def viewListBook(request):
    list_book = Book.objects.all()
    context = {"listBooks": list_book}
    return render(request, "services/book_list.html", context)


def create_borrowing(request):
    if request.method == 'POST':
        borrower_user_id = request.POST.get('borrower_user_id')
        borrowing_date = request.POST.get('borrowing_date')
        comment = request.POST.get('comment')
        status = request.POST.get('status')

        try:
            borrower_user = User.objects.get(id=borrower_user_id)
        except User.DoesNotExist:
            return JsonResponse({'message': 'Invalid borrower user ID.'}, status=400)
        if borrower_user:
            borrowing = Borrowing(
                borrower_user=borrower_user,
                borrowing_date=borrowing_date,
                comment=comment,
                status=status
            )
            borrowing.save()

        return JsonResponse({'message': 'Borrowing created successfully.'})
    else:
        return JsonResponse({'message': 'Invalid request method.'}, status=400)


def change_borrowing_status(request, borrowing_id):
    borrowing = get_object_or_404(Borrowing, id=borrowing_id)
    new_status = request.POST.get('status')

    if new_status is not None:
        borrowing.status = int(new_status)
        borrowing.save()
        return JsonResponse({'message': 'Status updated successfully.'})
    else:
        return JsonResponse({'message': 'Invalid status value.'}, status=400)

