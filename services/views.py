from django.contrib.auth.hashers import make_password
from django.db import transaction
from django.db.models import Count
from django.http import JsonResponse
from django.utils import timezone
from django_filters import rest_framework as filters
from rest_framework import generics, status
from rest_framework.filters import SearchFilter
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from services.managers.permission_manager import is_staff, IsStaff

from .models import Book, MemberBookCopy, Order, OrderDetail, User, BookCopy, BookClub, Member, Membership, \
    MembershipOrder, \
    MembershipOrderDetail, UploadFile, Category
from .serializers import BookCopySerializer, BookSerializer, GetOrderSerializer, OrderDetailSerializer, OrderSerializer, \
    UserLoginSerializer, UserRegisterSerializer, BookFilter, BookClubSerializer, BookClubRequestToJoinSerializer, \
    MemberSerializer, MembershipOrderSerializer, UserUpdateSerializer, MembershipSerializer, CategorySerializer, \
    MyBookAddSerializer, ShareBookClubSerializer, BookClubMemberUpdateSerializer


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
        for i, book_copy in enumerate(queryset):
            book_image = book_copy.book.image.name
            if 'fahasa.com' in book_image:
                data[i]['book']['image'] = book_image

        return Response(data)


class CategoryListView(generics.ListAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    pagination_class = CustomPagination


class BookClubMemberListView(generics.ListAPIView):
    permission_classes = (IsAuthenticated, IsStaff,)
    serializer_class = MemberSerializer
    pagination_class = CustomPagination

    def get_queryset(self):
        user_member = Member.objects.filter(user=self.request.user).first()
        if not user_member:
            return Response({'error': 'Staff is not club member'}, status=status.HTTP_400_BAD_REQUEST)
        queryset = Member.objects.filter(book_clubs__in=user_member.book_clubs.all())
        return queryset


class BookClubListAPIView(generics.ListAPIView):
    queryset = BookClub.objects.all()
    serializer_class = BookClubSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        data = serializer.data
        total_members = BookClub.objects.annotate(total_members=Count('member')).values('id', 'total_members')
        mapping_total_members = {r['id']: r['total_members'] for r in total_members}

        for i, book_club in enumerate(queryset):
            total_book_count = MemberBookCopy.objects.filter(membership__book_club=book_club).count()
            data[i]['total_member_count'] = mapping_total_members[book_club.id]
            data[i]['total_book_count'] = total_book_count

        return Response(data)


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
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            refresh = TokenObtainPairSerializer.get_token(user)
            data = {
                'refresh_token': str(refresh),
                'access_token': str(refresh.access_token),
                'user': {
                    'username': user.username,
                    'email': user.email,
                    'is_staff': is_staff(user),
                }
            }
            return Response(data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserRegisterView(APIView):
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
        avatar = request.user.avatar
        avatar_url = None
        if avatar:
            avatar_url = avatar.url.split('?')[0]

        data = {
            'username': request.user.username,
            'phone_number': request.user.phone_number,
            'email': request.user.email,
            'address': request.user.address,
            'full_name': request.user.full_name,
            'birth_date': request.user.birth_date,
            'avatar': avatar_url,
        }
        return Response(data)


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


class MemberShipOrderCreateView(APIView):
    permission_classes = (IsAuthenticated,)

    @transaction.atomic
    def post(self, request):
        serializer = MembershipOrderSerializer(data=request.data)
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
                    return Response({'result': 'ok'}, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BookShareClubView(APIView):
    permission_classes = (IsAuthenticated,)

    @transaction.atomic
    def post(self, request):
        serializer = ShareBookClubSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        club = BookClub.objects.filter(id=serializer.data['club_id']).first()
        if not club:
            return Response({'error': 'club not found'}, status=status.HTTP_400_BAD_REQUEST)

        membership = Membership.objects.filter(member__user=request.user, book_club=club).first()
        if not membership:
            return Response({'error': 'membership not found'}, status=status.HTTP_400_BAD_REQUEST)

        books = BookCopy.objects \
            .filter(user=request.user, id__in=serializer.data['book_copy_ids'], book_status=BookCopy.NEW).all()
        if len(books) != len(serializer.data['book_copy_ids']):
            return Response({'error': 'book not found'}, status=status.HTTP_400_BAD_REQUEST)

        BookCopy.objects \
            .filter(user=request.user, id__in=serializer.data['book_copy_ids'], book_status=BookCopy.NEW) \
            .update(updated_at=timezone.now(), book_status=BookCopy.SHARING_CLUB)

        member_book_copys = []
        for book in books:
            member_book_copys.append(MemberBookCopy(
                membership=membership,
                book_copy=book,
            ))
        MemberBookCopy.objects.bulk_create(member_book_copys)
        return Response({'result': 'ok'}, status=status.HTTP_201_CREATED)
