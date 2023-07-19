from django.db import IntegrityError
from django.utils import timezone
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from d_free_book.serializers import ClubBookGetIdsSerializer, ClubBookGetInfosSerializer, ClubBookAddSerializer, \
    GetOrderIdsSerializer, GetOrderInfosSerializer, OrderDetailGetIdsSerializer, OrderDetailGetInfosSerializer, \
    OrderCreateSerializer, MemberGetIdsSerializer, MemberGetInfosSerializer, MemberCreateSerializer, \
    MemberUpdateSerializer, ClubBookUpdateSerializer, OrderReturnBooksSerializer, OrderCreateNewMemberSerializer
from d_free_book import manager
from services.managers import membership_manager
from services.managers.book_manager import get_book_records
from services.managers.permission_manager import IsStaff

MAX_QUERY_SIZE = 300

class ClubBookGetIdsView(APIView):

    @swagger_auto_schema(request_body=ClubBookGetIdsSerializer)
    def post(self, request):
        serializer = ClubBookGetIdsSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        club_id = serializer.data.get('club_id')
        club_ids = serializer.data.get('club_ids')

        book_category_ids = serializer.data.get('book_category_ids')
        book_author_ids = serializer.data.get('book_author_ids')
        book_name = serializer.data.get('book_name')
        book_ids = get_book_records(author_ids=book_author_ids, category_ids=book_category_ids,
                                    book_name=book_name).pk_list()

        club_books = manager.get_club_book_records(club_id=club_id, club_ids=club_ids, book_ids=book_ids)
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
        return Response({'club_book_infos': club_book_infos.values()}, status=status.HTTP_200_OK)

class ClubBookAddView(APIView):
    permission_classes = (IsAuthenticated, IsStaff,)

    @swagger_auto_schema(request_body=ClubBookAddSerializer)
    def post(self, request):
        serializer = ClubBookAddSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        club_ids = membership_manager.get_membership_records(request.user, is_staff=True).flat_list('book_club_id')
        if serializer.data.get('club_id') not in club_ids:
            return Response({'error': 'Permission denied'}, status=status.HTTP_400_BAD_REQUEST)
        book = get_book_records(book_name=serializer.data.get('name')).first()

        if manager.get_club_book_records(code=serializer.data.get('code'), club_id=serializer.data.get('club_id')).exists():
            return Response({'error': 'Book code is duplicated'}, status=status.HTTP_400_BAD_REQUEST)

        manager.create_club_book(serializer.data, book)
        return Response({'result': 'create book successfully'}, status=status.HTTP_200_OK)

class ClubBookUpdateView(APIView):
    permission_classes = (IsAuthenticated, IsStaff,)

    @swagger_auto_schema(request_body=ClubBookUpdateSerializer)
    def post(self, request):
        serializer = ClubBookUpdateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        data = serializer.data
        club_ids = membership_manager.get_membership_records(request.user, is_staff=True).flat_list('book_club_id')
        club_book_id = data.pop('club_book_id')
        club_book = manager.get_club_book_records(
            club_book_ids=[club_book_id],
            club_ids=club_ids,
        ).first()

        if not club_book:
            return Response({'error': 'Book not found'}, status=status.HTTP_400_BAD_REQUEST)

        club_book_data = club_book.as_dict()
        updated_data = {}
        for k, v in data.items():
            if club_book_data.get(k) != v:
                updated_data[k] = v

        if updated_data.get('code') and manager.get_club_book_records(code=updated_data.get('code'), club_id=club_book.club_id).exists():
            return Response({'error': 'Book code is duplicated'}, status=status.HTTP_400_BAD_REQUEST)

        affected_count = manager.update_club_book(club_book_id, **updated_data)
        if affected_count:
            return Response({'message': 'Update Book successfully'}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Update Book failed'}, status=status.HTTP_400_BAD_REQUEST)

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

        club_ids = membership_manager.get_membership_records(request.user, is_staff=True).flat_list('book_club_id')
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

class OrderCreateView(APIView):
    permission_classes = (IsAuthenticated, IsStaff,)

    @swagger_auto_schema(request_body=OrderCreateSerializer)
    def post(self, request):
        serializer = OrderCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        manager.create_new_order(serializer.data)
        return Response({'message': 'Create order successfully'}, status=status.HTTP_200_OK)


class OrderCreateNewMemberView(APIView):
    permission_classes = (IsAuthenticated, IsStaff,)

    @swagger_auto_schema(request_body=OrderCreateNewMemberSerializer)
    def post(self, request):
        serializer = OrderCreateNewMemberSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        club_ids = membership_manager.get_membership_records(request.user, is_staff=True).flat_list('book_club_id')
        if serializer.data.get('club_id') not in club_ids:
            return Response({'error': 'Permission Denied'}, status=status.HTTP_400_BAD_REQUEST)

        exist_member = manager.get_member_records(
            code=serializer.data.get('new_member').get('code'),
            club_ids=[serializer.data.get('club_id')],
        ).exists()
        if exist_member:
            return Response({'error': 'Duplicated member code'}, status=status.HTTP_400_BAD_REQUEST)

        manager.create_new_order_by_new_member(serializer.data)
        return Response({'message': 'Create order successfully'}, status=status.HTTP_200_OK)

class OrderReturnBooksView(APIView):
    permission_classes = (IsAuthenticated, IsStaff,)

    @swagger_auto_schema(request_body=OrderReturnBooksSerializer)
    def post(self, request):
        serializer = OrderReturnBooksSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        order_detail_ids = serializer.data.get('order_detail_ids')
        return_date = serializer.data.get('return_date', timezone.now())
        manager.return_books(order_detail_ids, return_date)
        return Response({'message': 'Return books successfully'}, status=status.HTTP_200_OK)

class MemberGetIdsView(APIView):
    permission_classes = (IsAuthenticated, IsStaff,)

    @swagger_auto_schema(request_body=MemberGetIdsSerializer)
    def post(self, request):
        serializer = MemberGetIdsSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        club_ids = membership_manager.get_membership_records(request.user, is_staff=True).flat_list('book_club_id')
        member_ids = manager.get_member_records(
            club_ids=club_ids,
            code=serializer.data.get('code'),
            phone_number=serializer.data.get('phone_number'),
            full_name=serializer.data.get('full_name'),
        )[:MAX_QUERY_SIZE].pk_list()
        return Response({'member_ids': member_ids}, status=status.HTTP_200_OK)

class MemberGetInfosView(APIView):
    permission_classes = (IsAuthenticated, IsStaff,)

    @swagger_auto_schema(request_body=MemberGetInfosSerializer)
    def post(self, request):
        serializer = MemberGetInfosSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        member_ids = serializer.data.get('member_ids')
        member_infos = manager.get_member_infos(member_ids)
        return Response({'member_infos': member_infos.values()}, status=status.HTTP_200_OK)

class MemberAddView(APIView):
    permission_classes = (IsAuthenticated, IsStaff,)

    @swagger_auto_schema(request_body=MemberCreateSerializer)
    def post(self, request):
        serializer = MemberCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        club_ids = membership_manager.get_membership_records(request.user, is_staff=True).flat_list('book_club_id')
        if serializer.data.get('club_id') not in club_ids:
            return Response({'error': 'Invalid Club'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            manager.create_member(**serializer.data)
        except IntegrityError:
            return Response({'error': 'Duplicated member code'}, status=status.HTTP_400_BAD_REQUEST)

        return Response({'message': 'Create member successfully'}, status=status.HTTP_200_OK)

class MemberUpdateView(APIView):
    permission_classes = (IsAuthenticated, IsStaff,)

    @swagger_auto_schema(request_body=MemberUpdateSerializer)
    def post(self, request):
        serializer = MemberUpdateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        club_ids = membership_manager.get_membership_records(request.user, is_staff=True).flat_list('book_club_id')
        data = serializer.data
        member_id = data.pop('member_id')
        try:
            affected_count = manager.update_member(member_id, club_ids, **data)
        except IntegrityError:
            return Response({'error': 'Duplicated member code'}, status=status.HTTP_400_BAD_REQUEST)

        if affected_count:
            return Response({'message': 'Update member successfully'}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Update member failed'}, status=status.HTTP_400_BAD_REQUEST)
