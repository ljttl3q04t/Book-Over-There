from django.contrib.auth.hashers import make_password
from django.db import transaction
from django.db.models import Count
from django.http import JsonResponse
from django.utils import timezone
from django_filters import rest_framework as filters
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, status, serializers
from rest_framework.filters import SearchFilter
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken

from services.managers import membership_manager, book_manager
from services.managers.permission_manager import is_staff, IsStaff
from .managers.crawl_manager import CrawFahasa, CrawTiki
from .models import Book, MemberBookCopy, Order, OrderDetail, User, BookCopy, BookClub, Member, Membership, \
    MembershipOrder, \
    MembershipOrderDetail, UploadFile, Category, BookCopyHistory
from .serializers import BookCopySerializer, BookSerializer, GetOrderSerializer, OrderDetailSerializer, OrderSerializer, \
    UserLoginSerializer, UserRegisterSerializer, BookFilter, BookClubRequestToJoinSerializer, \
    MemberSerializer, MembershipOrderCreateSerializer, UserUpdateSerializer, MembershipSerializer, CategorySerializer, \
    MyBookAddSerializer, ShareBookClubSerializer, BookClubMemberUpdateSerializer, \
    UserSerializer, BookClubMemberDepositBookSerializer, BookClubMemberWithdrawBookSerializer, \
    BookClubStaffCreateOrderSerializer, MemberBookCopySerializer, ClubBookListFilter, BookCheckSerializer, \
    UserBorrowingBookSerializer, BookClubStaffExtendOrderSerializer, StaffBorrowingSerializer

class UploadFileView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        file = request.FILES['image_file']
        upload = UploadFile(file=file)
        upload.save()
        file_url = upload.file.url
        return Response({'file_url': file_url}, status=status.HTTP_200_OK)

class CustomPagination(PageNumberPagination):
    page_size = 10  # Set the desired page size
    page_size_query_param = 'page_size'  # Customize the query parameter for specifying the page size
    max_page_size = 100  # Set the maximum allowed page size

class BookListAPIView(generics.ListAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    pagination_class = CustomPagination
    filter_backends = [filters.DjangoFilterBackend, SearchFilter]
    filterset_class = BookFilter
    search_fields = ['name']

class ClubBookListAPIView(generics.ListAPIView):
    permission_classes = (IsAuthenticated, IsStaff,)
    serializer_class = MemberBookCopySerializer
    pagination_class = CustomPagination
    filter_backends = [filters.DjangoFilterBackend, SearchFilter]
    filterset_class = ClubBookListFilter

    search_fields = ['book_copy__book__name']

    def get_queryset(self):
        membership = Membership.objects.filter(member__user=self.request.user).first()
        if not membership:
            raise serializers.ValidationError("Membership not found")
        book_club = membership.book_club
        return MemberBookCopy.objects.filter(membership__book_club=book_club)

class MyBookView(generics.ListAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = BookCopy.objects.all()
    serializer_class = BookCopySerializer
    pagination_class = CustomPagination

    def get_queryset(self):
        return BookCopy.objects.filter(user=self.request.user)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        data = serializer.data
        return Response(data)

class CategoryListView(generics.ListAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    pagination_class = CustomPagination

class BookClubListAPIView(APIView):

    def get(self, request):
        map_clubs = membership_manager.get_clubs()
        data = map_clubs.values()
        for d in data:
            d['is_member'] = False

        if request.user.is_anonymous:
            return Response(data, status=status.HTTP_200_OK)
        else:
            joined_clubs = Membership.objects.filter(member__user=request.user).values_list('book_club_id', flat=True)
            total_members = BookClub.objects.annotate(total_members=Count('member')).values('id', 'total_members')
            mapping_total_members = {r['id']: r['total_members'] for r in total_members}

            for d in data:
                total_book_count = MemberBookCopy.objects.filter(membership__book_club_id=d['id']).count()
                d['total_member_count'] = mapping_total_members[d['id']]
                d['total_book_count'] = total_book_count
                d['is_member'] = d['id'] in joined_clubs
            return Response(data, status=status.HTTP_200_OK)

class LogoutView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        refresh_token = request.data.get('refresh_token')
        if refresh_token:
            try:
                token = RefreshToken(refresh_token)
                token.blacklist()
                return Response({'message': 'Logout successful.'}, status=status.HTTP_200_OK)
            except Exception as err:
                print(err)
                return Response({'error': 'Invalid token.'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'error': 'Refresh token is required.'}, status=status.HTTP_400_BAD_REQUEST)

class UserLoginView(APIView):
    @swagger_auto_schema(request_body=UserLoginSerializer)
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            refresh = TokenObtainPairSerializer.get_token(user)
            user_serializer = UserSerializer(instance=user)
            user_data = user_serializer.data
            user_data['is_staff'] = is_staff(user)

            data = {
                'refresh_token': str(refresh),
                'access_token': str(refresh.access_token),
                'user': user_data
            }
            return Response(data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserRegisterView(APIView):

    @swagger_auto_schema(request_body=UserRegisterSerializer)
    def post(self, request):
        serializer = UserRegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.validated_data['password'] = make_password(serializer.validated_data['password'])
            serializer.save()

            return JsonResponse({
                'message': 'Register successful!'
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserInfoView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user_serializer = UserSerializer(instance=request.user)
        user_data = user_serializer.data
        user_data['is_staff'] = is_staff(request.user)
        return Response(user_data, status=status.HTTP_200_OK)

class UpdateUserInfoView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):
        serializer = UserUpdateSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

class OverViewAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        data = {
            'user': User.objects.count(),
            'book': Book.objects.count(),
            'order': OrderDetail.objects.count(),
        }
        return JsonResponse(data, status=status.HTTP_200_OK)

class BookCheckView(APIView):
    permission_classes = (IsAuthenticated,)

    @swagger_auto_schema(request_body=BookCheckSerializer)
    def post(self, request):
        serializer = BookCheckSerializer(data=request.data)
        if serializer.is_valid():
            remote_url = serializer.data['remote_url']
            if remote_url.startswith(CrawFahasa.DOMAIN_PREFIX):
                crawler = CrawFahasa(remote_url)
            elif remote_url.startswith(CrawTiki.DOMAIN_PREFIX):
                crawler = CrawTiki(remote_url)
            else:
                return Response({'error': 'not support'}, status=status.HTTP_400_BAD_REQUEST)

            try:
                book = crawler.build_book()
            except:
                return Response({'error': 'check book failed'}, status=status.HTTP_200_OK)

            return Response(book, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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

class BookCopyCreateAPIView(APIView):
    def post(self, request):
        serializer = BookCopySerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class BookCopyUpdateView(APIView):
    def put(self, request, pk):
        try:
            book_copy = BookCopy.objects.get(pk=pk)
        except BookCopy.DoesNotExist:
            return Response({"error": "BookCopy not found."}, status=404)

        book_status = request.data.get('book_status')
        book_deposit_status = request.data.get('book_deposit_status')

        if book_status is not None:
            book_copy.book_status = book_status

        if book_deposit_status is not None:
            book_copy.book_deposit_status = book_deposit_status

        book_copy.save()

        return Response({"message": "BookCopy updated successfully."}, status=200)

# Oders
class OrderStatusUpdateAPIView(APIView):
    def patch(self, request, pk):
        try:
            order = Order.objects.get(pk=pk)
        except Order.DoesNotExist:
            return Response({"detail": "Order not found."}, status=status.HTTP_404_NOT_FOUND)

        order.status = request.data.get('status', order.status)
        order.save()

        serializer = OrderSerializer(order)
        return Response(serializer.data)

class OrderDetailCreateAPIView(APIView):
    def post(self, request):
        serializer = OrderDetailSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class OrderCreateAPIView(APIView):
    def post(self, request):
        serializer = OrderSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class GetOrderCreateAPIView(APIView):
    def get(self, request, order_id):
        try:
            order = Order.objects.prefetch_related('order_details').get(id=order_id)
            serializer = GetOrderSerializer(order)
            return Response(serializer.data)
        except Order.DoesNotExist:
            return Response({"error": "Order not found."}, status=404)

class BookClubRequestJoinView(APIView):
    permission_classes = (IsAuthenticated,)

    @transaction.atomic
    def post(self, request):
        serializer = BookClubRequestToJoinSerializer(data=request.data)
        if serializer.is_valid():
            try:
                club_id = request.data.get('club_id')
                book_club = BookClub.objects.get(id=club_id)
            except BookClub.DoesNotExist:
                return Response({"error": "Book club not found"}, status=status.HTTP_400_BAD_REQUEST)

            try:
                member = Member.objects.get(user=request.user)
            except Member.DoesNotExist:
                member_data = request.data.copy()
                member_data['user'] = request.user.id
                member_serializer = MemberSerializer(data=member_data)
                if member_serializer.is_valid():
                    member = member_serializer.save()
                else:
                    return Response(member_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            if book_club.membership_set.filter(member=member).exists():
                return Response({'error': 'User is already a member of this book club'},
                                status=status.HTTP_400_BAD_REQUEST)

            Membership.objects.create(member=member, book_club=book_club)
            return Response({"detail": "Membership request submitted."}, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class BookClubMemberView(APIView):
    permission_classes = (IsAuthenticated, IsStaff,)

    def get(self, request):
        club_ids = Membership.objects.filter(member__user=self.request.user, is_staff=True) \
            .values_list('book_club_id', flat=True)
        club_members = Membership.objects.filter(book_club__in=club_ids)
        serializer = MembershipSerializer(instance=club_members, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class BookClubMemberUpdateView(APIView):
    permission_classes = (IsAuthenticated, IsStaff,)

    @swagger_auto_schema(request_body=BookClubMemberUpdateSerializer)
    def post(self, request):
        serializer = BookClubMemberUpdateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            membership = Membership.objects.get(id=serializer.data['membership_id'])
        except Membership.DoesNotExist:
            return Response({'error': 'member not found'}, status=status.HTTP_400_BAD_REQUEST)

        if membership.member_status == Membership.PENDING and serializer.data['member_status'] == Membership.ACTIVE:
            membership.member_status = serializer.data['member_status']
            membership.save()
            return Response(MembershipSerializer(instance=membership).data, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'invalid change member status'}, status=status.HTTP_400_BAD_REQUEST)

class BookClubMemberBookDepositView(APIView):
    permission_classes = (IsAuthenticated, IsStaff,)

    @swagger_auto_schema(request_body=BookClubMemberDepositBookSerializer)
    @transaction.atomic
    def post(self, request):
        serializer = BookClubMemberDepositBookSerializer(data=request.data)
        description = request.data.get('description', '')
        attachment = request.data.get('attachment')

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        member_book_copy = serializer.validated_data
        history = BookCopyHistory.objects.create(
            book_copy=member_book_copy.book_copy,
            action=BookCopyHistory.DONATE_TO_CLUB,
            description=description,
            attachment=attachment,
        )
        member_book_copy.onboard_date = history.created_at
        member_book_copy.updated_at = history.created_at
        member_book_copy.save()
        return Response({'result': 'ok'}, status=status.HTTP_200_OK)

class BookClubMemberBookWithdrawView(APIView):
    permission_classes = (IsAuthenticated, IsStaff,)

    @swagger_auto_schema(request_body=BookClubMemberWithdrawBookSerializer)
    @transaction.atomic
    def post(self, request):
        serializer = BookClubMemberWithdrawBookSerializer(data=request.data)
        description = request.data.get('description', '')
        attachment = request.data.get('attachment')

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        member_book_copy = serializer.validated_data
        history = BookCopyHistory.objects.create(
            book_copy=member_book_copy.book_copy,
            action=BookCopyHistory.WITHDRAW_BOOK_FROM_CLUB,
            description=description,
            attachment=attachment,
        )

        member_book_copy.book_copy.book_status = BookCopy.NEW
        member_book_copy.book_copy.updated_at = history.created_at
        member_book_copy.save()

        member_book_copy.updated_at = history.created_at
        member_book_copy.is_enabled = False
        member_book_copy.onboard_date = None
        member_book_copy.save()
        return Response({'result': 'ok'}, status=status.HTTP_200_OK)

# class BookClubMemberBookLendView(APIView):
#     permission_classes = (IsAuthenticated, IsStaff,)
#
# class BookClubMemberBookReturnView(APIView):
#     permission_classes = (IsAuthenticated, IsStaff,)
#
#     @swagger_auto_schema(request_body=ReturnBookSerializer)
#     @transaction.atomic
#     def post(self, request):
#         serializer = ReturnBookSerializer(data=request.data)

class StaffBorrowingView(APIView):
    permission_classes = (IsAuthenticated, IsStaff,)

    @swagger_auto_schema(request_body=StaffBorrowingSerializer)
    def post(self, request):
        serializer = StaffBorrowingSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        membership = serializer.validated_data
        order_details = MembershipOrderDetail.objects.filter(order__membership=membership)
        serializer = UserBorrowingBookSerializer(instance=order_details, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class BookClubStaffExtendOrderView(APIView):
    permission_classes = (IsAuthenticated, IsStaff,)

    @swagger_auto_schema(request_body=BookClubStaffExtendOrderSerializer)
    @transaction.atomic
    def post(self, request):
        serializer = BookClubStaffExtendOrderSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        new_due_date = request.data['new_due_date']
        note = request.data['note']
        attachment = request.data.get('attachment')
        updated_at = timezone.now()

        order_details, membership_borrower, book_copy_ids = serializer.validated_data
        order_detail_ids = [o.id for o in order_details]

        MembershipOrderDetail.objects \
            .filter(id__in=order_detail_ids) \
            .update(due_date=new_due_date, updated_at=updated_at)

        history_list = [BookCopyHistory(
            book_copy_id=book_copy_id,
            action=BookCopyHistory.CLUB_EXTEND_DUE_DATE,
            membership_borrower=membership_borrower,
            description=note,
            attachment=attachment,
            created_at=updated_at,
        ) for book_copy_id in book_copy_ids]
        BookCopyHistory.objects.bulk_create(history_list)
        return Response({'result': 'ok'}, status=status.HTTP_200_OK)

class BookClubStaffCreateOrderView(APIView):
    permission_classes = (IsAuthenticated, IsStaff,)

    @swagger_auto_schema(request_body=BookClubStaffCreateOrderSerializer)
    @transaction.atomic
    def post(self, request):
        serializer = BookClubStaffCreateOrderSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        due_date = request.data['due_date']
        note = request.data['note']
        attachment = request.data.get('attachment')

        membership, member_book_copys = serializer.validated_data
        current_time = timezone.now()
        order = MembershipOrder.objects.create(
            membership=membership,
            order_date=current_time,
            confirm_date=current_time,
            order_status=MembershipOrder.CONFIRMED,
        )
        order_details = [
            MembershipOrderDetail(
                order=order,
                member_book_copy=member_book_copy,
                due_date=due_date,
            ) for member_book_copy in member_book_copys
        ]
        MembershipOrderDetail.objects.bulk_create(order_details)
        MemberBookCopy.objects.filter(id__in=request.data['member_book_copy_ids']) \
            .update(current_reader=membership, updated_at=current_time)
        book_copy_ids = [r.book_copy.id for r in member_book_copys]
        BookCopy.objects.filter(id__in=book_copy_ids).update(book_status=BookCopy.BORROWED, updated_at=current_time)
        history_list = [BookCopyHistory(
            book_copy_id=book_copy_id,
            action=BookCopyHistory.CLUB_BORROW_BOOK,
            membership_borrower=membership,
            description=note,
            attachment=attachment,
            created_at=current_time,
        ) for book_copy_id in book_copy_ids]
        BookCopyHistory.objects.bulk_create(history_list)
        return Response({'result': 'ok'}, status=status.HTTP_200_OK)

class BookClubBookListView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        user_clubs = membership_manager.get_user_club(request.user)
        records = MemberBookCopy.objects.filter(membership__book_club__in=user_clubs, current_reader=None)
        book_map = {}
        for r in records:
            book_id = r.book_copy.book.id
            book_data = book_map.get(book_id)
            if book_data:
                book_map[book_id]['total_copy_count'] += 1
            else:
                book_map[book_id] = {
                    'book': BookSerializer(instance=r.book_copy.book).data,
                    'club': r.membership.book_club_id,
                    'total_copy_count': 1,
                }
        return Response(book_map.values(), status=status.HTTP_200_OK)

class MemberShipOrderCreateView(APIView):
    permission_classes = (IsAuthenticated,)

    @swagger_auto_schema(request_body=MembershipOrderCreateSerializer)
    @transaction.atomic
    def post(self, request):
        serializer = MembershipOrderCreateSerializer(data=request.data)
        if serializer.is_valid():
            order_details = serializer.validated_data.pop('order_details')
            order = MembershipOrder.objects.create(
                membership_id=serializer.validated_data['membership_id']
            )
            for detail in order_details:
                MembershipOrderDetail.objects.create(
                    order_id=order.id,
                    member_book_copy_id=detail.member_book_copy_id,
                    due_date=detail.due_date,
                )
            return Response({'result': 'ok'}, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class MyMembershipView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        memberships = Membership.objects.filter(member__user=self.request.user)
        serializer = MembershipSerializer(memberships, many=True)
        return Response(serializer.data)

class MyBookAddView(APIView):
    permission_classes = (IsAuthenticated,)

    @swagger_auto_schema(request_body=MyBookAddSerializer)
    @transaction.atomic
    def post(self, request):
        serializer = MyBookAddSerializer(data=request.data)
        if serializer.is_valid():
            book_id = serializer.validated_data.get('book_id')
            if book_id:
                try:
                    book = Book.objects.get(id=book_id)
                except Book.DoesNotExist:
                    return Response({'error': 'book not found'}, status=status.HTTP_400_BAD_REQUEST)

                BookCopy.objects.create(
                    book=book,
                    user=request.user,
                )
                return Response({'result': 'ok'}, status=status.HTTP_201_CREATED)
            else:
                book_serializer = BookSerializer(data=serializer.validated_data.pop('book'))
                if book_serializer.is_valid():
                    book = book_serializer.save()
                    BookCopy.objects.create(
                        book=book,
                        user=request.user,
                    )
                    if book_serializer.validated_data.get('image_url'):
                        book_manager.save_image_from_url(book, book_serializer.validated_data.get('image_url'))
                    return Response({'result': 'ok'}, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class BookShareClubView(APIView):
    permission_classes = (IsAuthenticated,)

    @swagger_auto_schema(request_body=ShareBookClubSerializer)
    @transaction.atomic
    def post(self, request):
        serializer = ShareBookClubSerializer(data=request.data, context={'request': request})
        book_copy_ids = request.data.get('book_copy_ids')
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        membership, books = serializer.validated_data
        BookCopy.objects \
            .filter(user=request.user, id__in=book_copy_ids, book_status=BookCopy.NEW) \
            .update(updated_at=timezone.now(), book_status=BookCopy.SHARING_CLUB)

        member_book_copys = []
        for book in books:
            member_book_copys.append(MemberBookCopy(
                membership=membership,
                book_copy=book,
            ))
        MemberBookCopy.objects.bulk_create(member_book_copys)
        return Response({'result': 'ok'}, status=status.HTTP_201_CREATED)

class UserBorrowingBookView(APIView):
    permission_classes = (IsAuthenticated,)

    @transaction.atomic
    def get(self, request):
        user_memberships = membership_manager.get_membership_by_user(request.user)
        order_details = MembershipOrderDetail.objects.filter(order__membership__in=user_memberships)
        serializer = UserBorrowingBookSerializer(instance=order_details, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
