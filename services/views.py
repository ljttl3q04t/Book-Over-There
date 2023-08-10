from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password
from django.contrib.auth.tokens import default_token_generator
from django.db import transaction
from django.db.models import Count
from django.http import JsonResponse
from django.shortcuts import resolve_url
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django_filters import rest_framework as filters
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, serializers, status
from rest_framework.filters import SearchFilter
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken

from d_free_book.manager import link_user_member
from d_free_book.serializers import ClubStaffSerializer
from services.managers import book_manager, membership_manager, otp_manager
from services.managers.permission_manager import IsStaff, is_club_admin
from .managers.book_manager import get_category_infos
from .managers.crawl_manager import CrawFahasa, CrawTiki
from .managers.email_manager import send_password_reset_email
from .models import Book, BookClub, BookCopy, BookCopyHistory, Member, MemberBookCopy, Membership, MembershipOrder, \
    MembershipOrderDetail, UploadFile, User
from .serializers import BookCheckSerializer, BookClubMemberDepositBookSerializer, BookClubMemberUpdateSerializer, \
    BookClubMemberWithdrawBookSerializer, BookClubRequestToJoinSerializer, BookClubStaffCreateOrderSerializer, \
    BookClubStaffExtendOrderSerializer, BookCopyHistorySerializer, BookCopySerializer, BookFilter, BookSerializer, \
    ClubBookListFilter, MemberBookCopySerializer, MemberSerializer, MembershipOrderCreateSerializer, \
    MembershipSerializer, MyBookAddSerializer, PasswordResetConfirmSerializer, PasswordResetSerializer, \
    ReturnBookSerializer, ShareBookClubSerializer, StaffBorrowingSerializer, StaffOrderConfirmSerializer, \
    UserBorrowingBookSerializer, UserChangePasswordSerializer, UserLoginSerializer, UserRegisterSerializer, \
    UserSerializer, UserUpdateSerializer

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

class CategoryListView(APIView):

    def get(self, request, follower):
        category_infos = get_category_infos().values()
        data = [category for category in category_infos if category.get('follower') == follower]
        return Response({'result': data}, status=status.HTTP_200_OK)

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

class UserChangePasswordView(APIView):
    def post(self, request):
        serializer = UserChangePasswordSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_200_OK)

        user = authenticate(username=request.user.username, password=serializer.data.get('password'))
        if not user:
            raise serializers.ValidationError('Invalid username or password.')
        user.set_password(serializer.data.get('new_password'))
        user.save()
        return Response({'message': 'Password reset successful.'}, status=status.HTTP_200_OK)

class ResetPasswordView(APIView):

    @swagger_auto_schema(request_body=PasswordResetSerializer)
    def post(self, request):
        serializer = PasswordResetSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        user = serializer.validated_data['username_or_email']
        token_generator = default_token_generator
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = token_generator.make_token(user)
        reset_url = reverse_lazy('reset_password_confirm', kwargs={'uidb64': uid, 'token': token})
        reset_url = reset_url.replace('/services', '')
        url = resolve_url(reset_url)
        absolute_uri = request.build_absolute_uri(url)
        send_password_reset_email.delay(user.email, absolute_uri)
        return Response(
            {'message': 'We have sent you an e-mail. Please contact us if you do not receive it within a few minutes.'},
            status=status.HTTP_200_OK)

class ResetPasswordConfirmView(APIView):

    @swagger_auto_schema(request_body=PasswordResetConfirmSerializer)
    def post(self, request, uidb64, token):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return Response({'error': 'Invalid password reset link.'}, status=status.HTTP_400_BAD_REQUEST)

        token_generator = default_token_generator
        if not token_generator.check_token(user, token):
            return Response({'error': 'Invalid token.'}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(serializer.validated_data['new_password'])
        user.save()

        return Response({'message': 'Password reset successful.'}, status=status.HTTP_200_OK)

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
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(phone_number=serializer.validated_data.get('phone_number')).exists():
            return Response({'error': 'Duplicated phone number'}, status=status.HTTP_400_BAD_REQUEST)

        serializer.validated_data['password'] = make_password(serializer.validated_data['password'])
        serializer.save()

        return Response({
            'message': 'Register successful!'
        }, status=status.HTTP_201_CREATED)

class UserInfoView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user_serializer = UserSerializer(instance=request.user)
        user_data = user_serializer.data
        return Response(user_data, status=status.HTTP_200_OK)

class UpdateUserInfoView(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def put(self, request):
        serializer = UserUpdateSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            change_phone_number = serializer.validated_data.get('phone_number')
            if change_phone_number:
                if User.objects.filter(phone_number=change_phone_number).exists():
                    return Response({'error': 'Duplicated phone number'}, status=status.HTTP_400_BAD_REQUEST)
            for attr, value in serializer.validated_data.items():
                setattr(serializer, attr, value)
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

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

    def post(self, request):
        serializer = ClubStaffSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        club_members = Membership.objects.filter(book_club_id=serializer.validated_data.get('club_id'))
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
        if "member_status" in serializer.data:
            if membership.member_status == Membership.PENDING and serializer.data['member_status'] == Membership.ACTIVE:
                membership.member_status = serializer.data['member_status']
                membership.save()
                return Response({'message': "Approve successfully"}, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'invalid change member status'}, status=status.HTTP_400_BAD_REQUEST)
        if 'is_staff' in serializer.data:
            if is_club_admin(request.user):
                membership.is_staff = serializer.data['is_staff']
                membership.save()
                return Response({'message': 'Update staff successfully'}, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'You cant update status staff'}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'error': 'An error occurred'}, status=status.HTTP_400_BAD_REQUEST)

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

        member_book_copys = serializer.validated_data
        updated_at = timezone.now()
        member_book_copy_ids = [r.id for r in member_book_copys]
        book_copy_ids = [r.book_copy.id for r in member_book_copys]
        MemberBookCopy.objects \
            .filter(id__in=member_book_copy_ids) \
            .update(updated_at=updated_at, onboard_date=updated_at)

        BookCopy.objects.filter(id__in=book_copy_ids).update(book_status=BookCopy.SHARING_CLUB, updated_at=updated_at)

        attachment_file = None
        if attachment:
            attachment_file = UploadFile.objects.create(file=attachment)

        history_list = [BookCopyHistory(
            book_copy_id=book_copy_id,
            action=BookCopyHistory.DONATE_TO_CLUB,
            description=description,
            attachment=attachment_file,
            created_at=updated_at,
        ) for book_copy_id in book_copy_ids]
        BookCopyHistory.objects.bulk_create(history_list)
        return Response({'result': 'deposit books successfully'}, status=status.HTTP_200_OK)

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

        member_book_copys = serializer.validated_data
        updated_at = timezone.now()
        member_book_copy_ids = [r.id for r in member_book_copys]
        book_copy_ids = [r.book_copy.id for r in member_book_copys]
        MemberBookCopy.objects \
            .filter(id__in=member_book_copy_ids) \
            .update(updated_at=updated_at, is_enabled=False, onboard_date=None)

        BookCopy.objects.filter(id__in=book_copy_ids).update(book_status=BookCopy.NEW, updated_at=updated_at)

        attachment_file = None
        if attachment:
            attachment_file = UploadFile.objects.create(file=attachment)

        history_list = [BookCopyHistory(
            book_copy_id=book_copy_id,
            action=BookCopyHistory.WITHDRAW_BOOK_FROM_CLUB,
            description=description,
            attachment=attachment_file,
            created_at=updated_at,
        ) for book_copy_id in book_copy_ids]
        BookCopyHistory.objects.bulk_create(history_list)
        return Response({'result': 'withdraw books successfully'}, status=status.HTTP_200_OK)

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

class BookClubMemberBookReturnView(APIView):
    permission_classes = (IsAuthenticated, IsStaff,)

    @swagger_auto_schema(request_body=ReturnBookSerializer)
    @transaction.atomic
    def post(self, request):
        serializer = ReturnBookSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        note = request.data['note']
        attachment = request.data.get('attachment')
        updated_at = timezone.now()

        order_details, membership_borrower, book_copy_ids = serializer.validated_data
        order_detail_ids = [o.id for o in order_details]
        member_book_copy_ids = [o.member_book_copy_id for o in order_details]

        MembershipOrderDetail.objects \
            .filter(id__in=order_detail_ids) \
            .update(return_date=updated_at, updated_at=updated_at)

        MemberBookCopy.objects.filter(id__in=member_book_copy_ids).update(updated_at=updated_at, current_reader=None)
        BookCopy.objects.filter(id__in=book_copy_ids).update(updated_at=updated_at, book_status=BookCopy.SHARING_CLUB)
        order_ids = set([o.order_id for o in order_details])
        for order_id in order_ids:
            flag = MembershipOrderDetail.objects.filter(order_id=order_id, return_date__isnull=True).exists()
            if not flag:
                MembershipOrder.objects.filter(id=order_id).update(updated_at=updated_at,
                                                                   order_status=MembershipOrder.COMPLETED)

        attachment_file = None
        if attachment:
            attachment_file = UploadFile.objects.create(file=attachment)

        history_list = [BookCopyHistory(
            book_copy_id=book_copy_id,
            action=BookCopyHistory.CLUB_RETURN_BOOK,
            membership_borrower=membership_borrower,
            description=note,
            attachment=attachment_file,
            created_at=updated_at,
        ) for book_copy_id in book_copy_ids]
        BookCopyHistory.objects.bulk_create(history_list)
        return Response({'result': 'return books successfully'}, status=status.HTTP_200_OK)

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

        attachment_file = None
        if attachment:
            attachment_file = UploadFile.objects.create(file=attachment)

        history_list = [BookCopyHistory(
            book_copy_id=book_copy_id,
            action=BookCopyHistory.CLUB_EXTEND_DUE_DATE,
            membership_borrower=membership_borrower,
            description=note,
            attachment=attachment_file,
            created_at=updated_at,
        ) for book_copy_id in book_copy_ids]
        BookCopyHistory.objects.bulk_create(history_list)
        return Response({'result': 'ok'}, status=status.HTTP_200_OK)

class StaffConfirmOrderView(APIView):
    permission_classes = (IsAuthenticated, IsStaff,)

    @swagger_auto_schema(request_body=StaffOrderConfirmSerializer)
    @transaction.atomic
    def post(self, request):
        serializer = StaffOrderConfirmSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        order = serializer.validated_data
        note = request.data['note']
        attachment = request.data.get('attachment')
        updated_at = timezone.now()

        MembershipOrder.objects \
            .filter(id=order.id) \
            .update(order_status=MembershipOrder.CONFIRMED, updated_at=updated_at, confirm_date=updated_at)

        member_book_copy_ids = MembershipOrderDetail.objects.filter(order_id=order.id).values_list(
            'member_book_copy_id', flat=True)
        book_copy_ids = MemberBookCopy.objects.filter(id__in=member_book_copy_ids).values_list('book_copy_id',
                                                                                               flat=True)

        MemberBookCopy.objects \
            .filter(id__in=member_book_copy_ids) \
            .update(current_reader=order.membership, updated_at=updated_at)

        BookCopy.objects.filter(id__in=book_copy_ids).update(updated_at=updated_at, book_status=BookCopy.BORROWED)

        attachment_file = None
        if attachment:
            attachment_file = UploadFile.objects.create(file=attachment)

        history_list = [BookCopyHistory(
            book_copy_id=book_copy_id,
            action=BookCopyHistory.CLUB_EXTEND_DUE_DATE,
            membership_borrower=order.membership,
            description=note,
            attachment=attachment_file,
            created_at=updated_at,
        ) for book_copy_id in book_copy_ids]
        BookCopyHistory.objects.bulk_create(history_list)
        return Response({'result': 'Order confirmed'}, status=status.HTTP_200_OK)

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
        attachment_file = None
        if attachment:
            attachment_file = UploadFile.objects.create(file=attachment)

        history_list = [BookCopyHistory(
            book_copy_id=book_copy_id,
            action=BookCopyHistory.CLUB_BORROW_BOOK,
            membership_borrower=membership,
            description=note,
            attachment=attachment_file,
            created_at=current_time,
        ) for book_copy_id in book_copy_ids]
        BookCopyHistory.objects.bulk_create(history_list)
        return Response({'result': 'ok'}, status=status.HTTP_200_OK)

class BookClubBookListView(APIView):
    # permission_classes = (IsAuthenticated,)

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
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        order_details = serializer.validated_data.pop('order_details')
        order = MembershipOrder.objects.create(
            membership_id=serializer.validated_data['membership_id'],
        )
        for detail in order_details:
            MembershipOrderDetail.objects.create(
                order=order,
                member_book_copy=detail['member_book_copy'],
                due_date=detail['due_date'],
            )
        return Response({'result': 'create order successfully'}, status=status.HTTP_201_CREATED)

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

class BookHistoryView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        book_copys = BookCopy.objects.filter(user=request.user)
        records = BookCopyHistory.objects.filter(book_copy__in=book_copys)
        serializer = BookCopyHistorySerializer(instance=records, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class OtpGenerateView(APIView):
    permission_classes = (IsAuthenticated, )

    def post(self, request):
        phone_number = request.user.phone_number
        if not phone_number:
            return Response({'error': 'user has no phone number'}, status=status.HTTP_400_BAD_REQUEST)
        otp_manager.remove_expired_otp(phone_number)
        new_otp, error = otp_manager.generate_otp(phone_number)
        if error:
            return Response({'error': error}, status=status.HTTP_400_BAD_REQUEST)
        try:
            otp_manager.send_otp(new_otp)
        except Exception:
            return Response({'error': 'send otp failed. Try again!'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({'message': "send otp successful"}, status=status.HTTP_200_OK)

class OtpVerifyView(APIView):
    permission_classes = (IsAuthenticated, )

    def post(self, request, otp_code):
        phone_number = request.user.phone_number
        if not phone_number:
            return Response({'error': 'user has no phone number'}, status=status.HTTP_400_BAD_REQUEST)
        result, error = otp_manager.verify_otp_code(phone_number, otp_code)
        if not result:
            return Response({'error': error}, status=status.HTTP_400_BAD_REQUEST)
        else:
            link_user_member(request.user)
            return Response({'message': 'verify OTP success'}, status=status.HTTP_200_OK)
