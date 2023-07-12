from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from d_free_book.serializers import ClubBookGetIdsSerializer, ClubBookGetInfosSerializer, ClubBookAddSerializer, \
    GetOrderIdsSerializer
from d_free_book import manager
from services.managers.book_manager import get_book_records
from services.managers.permission_manager import IsStaff

MAX_QUERY_SIZE = 2000

class ClubBookGetIdsView(APIView):

    @swagger_auto_schema(request_body=ClubBookGetIdsSerializer)
    def post(self, request):
        serializer = ClubBookGetIdsSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        club_id = serializer.data['club_id']

        book_category_ids = serializer.data.get('book_category_ids')
        book_author_ids = serializer.data.get('book_author_ids')
        book_name = serializer.data.get('book_name')
        book_ids = get_book_records(author_ids=book_author_ids, category_ids=book_category_ids, book_name=book_name).pk_list()

        club_books = manager.get_club_book_records(club_id=club_id, book_ids=book_ids)
        club_book_ids = club_books.order_by('-id')[:MAX_QUERY_SIZE].pk_list()
        return Response({'club_book_ids': club_book_ids}, status=status.HTTP_200_OK)

class ClubBookGetInfosView(APIView):

    @swagger_auto_schema(request_body=ClubBookGetInfosSerializer)
    def post(self, request):
        serializer = ClubBookGetInfosSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        club_book_ids = serializer.data['club_book_ids']
        club_book_infos = manager.get_club_book_infos(club_book_ids)
        return Response({'club_book_infos': club_book_infos}, status=status.HTTP_200_OK)

class StaffAddBook(APIView):
    permission_classes = (IsAuthenticated, IsStaff,)

    def post(self, request):
        serializer = ClubBookAddSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class StaffGetOrderIdsView(APIView):
    permission_classes = (IsAuthenticated, IsStaff,)

    def post(self, request):
        serializer = ClubBookAddSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class OrderInfosView(APIView):
    permission_classes = (IsAuthenticated, IsStaff,)

    def post(self, request):
        serializer = GetOrderIdsSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        