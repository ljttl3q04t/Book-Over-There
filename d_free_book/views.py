from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from d_free_book.serializers import ClubBookGetIdsSerializer, ClubBookGetInfosSerializer
from d_free_book import manager

MAX_QUERY_SIZE = 2000

class ClubBookGetIdsView(APIView):
    def post(self, request):
        serializer = ClubBookGetIdsSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        club_id = serializer.data['club_id']
        club_books = manager.get_club_book_records(club_id=club_id)
        club_book_ids = club_books.order_by('-id')[:MAX_QUERY_SIZE].pk_list()
        return Response({'club_book_ids': club_book_ids}, status=status.HTTP_200_OK)

class ClubBookGetInfosView(APIView):
    def post(self, request):
        serializer = ClubBookGetInfosSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        club_book_ids = serializer.data['club_book_ids']
        club_books = manager.get_club_book_records(club_id=club_id)
        club_book_ids = club_books.order_by('-id')[:MAX_QUERY_SIZE].pk_list()
        return Response({'club_book_ids': club_book_ids}, status=status.HTTP_200_OK)