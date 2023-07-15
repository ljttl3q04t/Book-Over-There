from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from d_free_book.serializers import ClubBookGetIdsSerializer, ClubBookGetInfosSerializer, ClubBookAddSerializer, \
    GetOrderIdsSerializer, GetOrderInfosSerializer, OrderDetailGetIdsSerializer, OrderDetailGetInfosSerializer
from d_free_book import manager
from services.managers import membership_manager
from services.managers.book_manager import get_book_records
from services.managers.permission_manager import IsStaff

MAX_QUERY_SIZE = 2000

class ClubBookGetIdsView(APIView):

    @swagger_auto_schema(request_body=ClubBookGetIdsSerializer)
    def post(self, request):
        serializer = ClubBookGetIdsSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        club_id = serializer.data.get('club_id')

        book_category_ids = serializer.data.get('book_category_ids')
        book_author_ids = serializer.data.get('book_author_ids')
        book_name = serializer.data.get('book_name')
        book_ids = get_book_records(author_ids=book_author_ids, category_ids=book_category_ids,
                                    book_name=book_name).pk_list()

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

class ClubBookAddView(APIView):
    permission_classes = (IsAuthenticated, IsStaff,)

    @swagger_auto_schema(request_body=ClubBookAddSerializer)
    def post(self, request):
        serializer = ClubBookAddSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        if get_book_records(serializer.data['name']).exists():
            return Response({'error': 'Book already exists'}, status=status.HTTP_400_BAD_REQUEST)
        manager.create_club_book(serializer.data)
        return Response({'result': 'create book successfully'}, status=status.HTTP_200_OK)

# class ClubBookUpdateView(APIView):
#     permission_classes = (IsAuthenticated, IsStaff,)
#
#     @swagger_auto_schema(request_body=ClubBookAddSerializer)
#     def post(self, request):
#         serializer = ClubBookAddSerializer(data=request.data)
#         if not serializer.is_valid():
#             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#         if get_book_records(serializer.data['name']).exists():
#             return Response({'error': 'Book already exists'}, status=status.HTTP_400_BAD_REQUEST)
#         manager.create_club_book(serializer.data)
#         return Response({'result': 'create book successfully'}, status=status.HTTP_200_OK)

class OrderDetailGetIdsView(APIView):
    # permission_classes = (IsAuthenticated, IsStaff,)

    @swagger_auto_schema(request_body=OrderDetailGetIdsSerializer)
    def post(self, request):
        serializer = OrderDetailGetIdsSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        club_id = serializer.data['club_id']
        from_date = serializer.data.get('from_date')
        to_date = serializer.data.get('to_date')

        order_ids = manager.get_order_records(club_id=club_id, from_date=from_date, to_date=to_date).pk_list()
        order_detail_ids = manager.get_order_detail_records(order_ids=order_ids).pk_list()
        return Response({'order_detail_ids': order_detail_ids}, status=status.HTTP_200_OK)

class OrderDetailGetInfosView(APIView):
    # permission_classes = (IsAuthenticated, IsStaff,)

    @swagger_auto_schema(request_body=OrderDetailGetInfosSerializer)
    def post(self, request):
        serializer = OrderDetailGetInfosSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        order_detail_infos = manager.get_order_detail_infos(serializer.data['order_detail_ids'])
        return Response({'order_detail_infos': order_detail_infos.values()}, status=status.HTTP_200_OK)

class StaffGetOrderIdsView(APIView):
    permission_classes = (IsAuthenticated, IsStaff,)

    @swagger_auto_schema(request_body=GetOrderIdsSerializer)
    def post(self, request):
        serializer = GetOrderIdsSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        club_ids = membership_manager.get_membership_records(request.user, is_staff=True).flat_list('book_club_id', flat=True)
        from_date = serializer.data.get('from_date')
        to_date = serializer.data.get('to_date')
        order_ids = manager.get_order_records(club_ids=club_ids, from_date=from_date, to_date=to_date).pk_list()
        return Response({'order_ids': order_ids}, status=status.HTTP_200_OK)

class OrderInfosView(APIView):
    permission_classes = (IsAuthenticated, IsStaff,)

    @swagger_auto_schema(request_body=GetOrderInfosSerializer)
    def post(self, request):
        serializer = GetOrderInfosSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        order_infos = manager.get_order_infos(serializer.data['order_ids'])
        return Response({'order_infos': order_infos.values()}, status=status.HTTP_200_OK)
