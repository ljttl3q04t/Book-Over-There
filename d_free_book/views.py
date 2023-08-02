from django.db import IntegrityError
from django.utils import timezone
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from d_free_book import manager
from d_free_book.serializers import ClubBookGetIdsSerializer, ClubBookGetInfosSerializer, ClubBookAddSerializer, \
    GetOrderIdsSerializer, GetOrderInfosSerializer, OrderCreateSerializer, MemberGetIdsSerializer, \
    MemberGetInfosSerializer, MemberCreateSerializer, \
    MemberUpdateSerializer, ClubBookUpdateSerializer, OrderReturnBooksSerializer, OrderCreateNewMemberSerializer, \
    DraftOrderCreateSerializer, GetDraftOrderInfosSerializer, MemberCheckSerializer, OrderCreateFromDraftSerializer, \
    OrderCreateFromDraftNewMemberSerializer, DraftOrderUpdateSerializer
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
        # club_book_ids = club_books.order_by('-id')[:MAX_QUERY_SIZE].pk_list()
        club_book_ids = club_books.pk_list()
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

        if manager.get_club_book_records(code=serializer.data.get('code'),
                                         club_id=serializer.data.get('club_id')).exists():
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

        if updated_data.get('code') and manager.get_club_book_records(code=updated_data.get('code'),
                                                                      club_id=club_book.club_id).exists():
            return Response({'error': 'Book code is duplicated'}, status=status.HTTP_400_BAD_REQUEST)

        affected_count = manager.update_club_book(club_book_id, **updated_data)
        if affected_count:
            return Response({'message': 'Update Book successfully'}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Update Book failed'}, status=status.HTTP_400_BAD_REQUEST)

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
        order_date = serializer.data.get('order_date')
        order_status = serializer.data.get('order_status')
        order_ids = manager \
            .get_order_records(club_ids=club_ids, from_date=from_date, to_date=to_date, order_date=order_date) \
            .order_by('-order_date', '-id') \
            .pk_list()
        if order_status:
            order_ids = manager.get_order_detail_records(order_ids=order_ids, order_status=order_status).flat_list(
                'order_id')
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

class GetDraftOrderIdsView(APIView):
    permission_classes = (IsAuthenticated, IsStaff,)

    def post(self, request):
        club_ids = membership_manager.get_membership_records(request.user, is_staff=True).flat_list('book_club_id')
        draft_order_ids = manager.get_draft_order_records(club_ids=club_ids).pk_list()
        return Response({'draft_order_ids': draft_order_ids}, status=status.HTTP_200_OK)

class GetDraftOrderInfosView(APIView):
    permission_classes = (IsAuthenticated,)

    @swagger_auto_schema(request_body=GetDraftOrderInfosSerializer)
    def post(self, request):
        serializer = GetDraftOrderInfosSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        draft_order_infos = manager.get_draft_order_infos(serializer.data.get('draft_order_ids'))
        return Response({'draft_order_infos': draft_order_infos.values()}, status=status.HTTP_200_OK)

class OrderCreateView(APIView):
    permission_classes = (IsAuthenticated, IsStaff,)

    @swagger_auto_schema(request_body=OrderCreateSerializer)
    def post(self, request):
        serializer = OrderCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        validate_oder, error = manager.validate_oder(serializer.data)
        if not validate_oder:
            return Response({'error': error}, status=status.HTTP_400_BAD_REQUEST)

        manager.create_new_order(serializer.data)
        return Response({'message': 'Create order successfully'}, status=status.HTTP_200_OK)

class DraftOrderCreateOnlineView(APIView):
    permission_classes = (IsAuthenticated,)

    @swagger_auto_schema(request_body=DraftOrderCreateSerializer)
    def post(self, request):
        serializer = DraftOrderCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        manager.create_new_draft_order(serializer.data)
        return Response({'message': 'Create draft order successfully'}, status=status.HTTP_200_OK)

class DraftOrderUpdateOnlineView(APIView):
    permission_classes = (IsAuthenticated, IsStaff,)

    @swagger_auto_schema(request_body=DraftOrderUpdateSerializer)
    def post(self, request):
        serializer = DraftOrderUpdateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.data
        draft_order_id = data.pop('draft_order_id')
        affected_count = manager.update_draft(draft_order_id, **data)
        if affected_count:
            return Response({'message': 'Update draft successfully'}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Update draft failed'}, status=status.HTTP_400_BAD_REQUEST)

class OrderCreateNewMemberView(APIView):
    permission_classes = (IsAuthenticated, IsStaff,)

    @swagger_auto_schema(request_body=OrderCreateNewMemberSerializer)
    def post(self, request):
        serializer = OrderCreateNewMemberSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        club_ids = membership_manager.get_membership_records(request.user, is_staff=True).flat_list('book_club_id')
        club_id = serializer.data.get('new_member').get('club_id')
        if club_id not in club_ids:
            return Response({'error': 'Permission Denied'}, status=status.HTTP_400_BAD_REQUEST)

        valid_member, error = manager.validate_member(
            club_id=club_id,
            phone_number=serializer.data.get('new_member').get('phone_number'),
            code=serializer.data.get('new_member').get('code'),
        )
        if not valid_member:
            return Response({'error': error}, status=status.HTTP_400_BAD_REQUEST)
        else:
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
        receiver_id = serializer.data.get('receiver_id')
        return_date = serializer.data.get('return_date', timezone.now())
        manager.return_books(order_detail_ids, return_date, receiver_id)
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
        ).pk_list()
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

        valid_member, error = manager.validate_member(club_id=serializer.data.get('club_id'),
                                                      phone_number=serializer.data.get('phone_number'),
                                                      code=serializer.data.get('code'), )
        if not valid_member:
            return Response({'error': error}, status=status.HTTP_400_BAD_REQUEST)
        else:
            manager.create_member(**serializer.data)

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

        member = manager.get_member_records(member_id=member_id, club_ids=club_ids).first()
        if not member:
            return Response({'error': 'Member not found'}, status=status.HTTP_200_OK)

        member_data = member.as_dict()
        updated_data = {}
        for k, v in data.items():
            if member_data.get(k) != v:
                updated_data[k] = v

        valid_member, error = manager.validate_member(club_id=member.club_id, **updated_data)
        if not valid_member:
            return Response({'error': error}, status=status.HTTP_400_BAD_REQUEST)
        else:
            affected_count = manager.update_member(member_id, **updated_data)
            if affected_count:
                return Response({'message': 'Update member successfully'}, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Update member failed'}, status=status.HTTP_400_BAD_REQUEST)

class MemberCheckView(APIView):
    permission_classes = (IsAuthenticated, IsStaff,)

    @swagger_auto_schema(request_body=MemberCheckSerializer)
    def post(self, request):
        serializer = MemberCheckSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        check_member, status_member = manager.check_member(phone_number=serializer.data.get('phone_number'),
                                                           club_id=serializer.data.get('club_id'))
        if check_member:
            return Response({'status_member': status_member})
        else:
            return Response({'status_member': status_member})

class OrderCreateFromDraftView(APIView):
    permission_classes = (IsAuthenticated, IsStaff,)

    @swagger_auto_schema(request_body=OrderCreateFromDraftSerializer)
    def post(self, request):
        serializer = OrderCreateFromDraftSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        validate_oder, error = manager.validate_oder(serializer.data)
        if not validate_oder:
            return Response({'error': error}, status=status.HTTP_400_BAD_REQUEST)

        manager.create_new_order_from_draft(serializer.data)
        return Response({'message': 'Create order successfully'}, status=status.HTTP_200_OK)

class OrderCreateFromDraftNewMemberView(APIView):
    permission_classes = (IsAuthenticated, IsStaff,)

    @swagger_auto_schema(request_body=OrderCreateFromDraftNewMemberSerializer)
    def post(self, request):
        serializer = OrderCreateFromDraftNewMemberSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        club_ids = membership_manager.get_membership_records(request.user, is_staff=True).flat_list('book_club_id')
        club_id = serializer.data.get('new_member').get('club_id')
        if club_id not in club_ids:
            return Response({'error': 'Permission Denied'}, status=status.HTTP_400_BAD_REQUEST)

        valid_member, error = manager.validate_member(
            club_id=club_id,
            phone_number=serializer.data.get('new_member').get('phone_number'),
            code=serializer.data.get('new_member').get('code'),
        )
        if not valid_member:
            return Response({'error': error}, status=status.HTTP_400_BAD_REQUEST)
        else:
            manager.create_new_order_from_draft_by_new_member(serializer.data)
            return Response({'message': 'Create order successfully'}, status=status.HTTP_200_OK)

class UserOrderHistoryView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        member_ids = manager.get_member_records(user_id=request.user.id).pk_list()
        order_ids = manager.get_order_records(member_ids=member_ids).pk_list()
        order_infos = manager.get_order_infos(order_ids)
        return Response({'order_infos': order_infos.values()}, status=status.HTTP_200_OK)

class ReportView(APIView):
    permission_classes = (IsAuthenticated, IsStaff,)

    def post(self, request, club_id):
        return Response({'data': manager.gen_report(club_id)}, status=status.HTTP_200_OK)
