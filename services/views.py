from django.contrib.auth.hashers import make_password
from django.db import transaction
from django.db.models import Count
from django.http import JsonResponse
from django_filters import rest_framework as filters
from rest_framework import generics, status
from rest_framework.filters import SearchFilter
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Book, MemberBookCopy, Order, OrderDetail, User, BookCopy, BookClub, Member, Membership, \
    MembershipOrder, \
    MembershipOrderDetail
from .serializers import BookCopySerializer, BookSerializer, GetOrderSerializer, OrderDetailSerializer, OrderSerializer, \
    UserLoginSerializer, UserSerializer, BookFilter, BookClubSerializer, BookClubRequestToJoinSerializer, \
    MemberSerializer, MembershipOrderSerializer

class CustomPagination(PageNumberPagination):
    page_size = 10  # Set the desired page size
    page_size_query_param = 'page_size'  # Customize the query parameter for specifying the page size
    max_page_size = 100  # Set the maximum allowed page size

class BookListAPIView(generics.ListAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    pagination_class = CustomPagination
    filter_backends = [filters.DjangoFilterBackend, SearchFilter]
    filterset_class = BookFilter
    search_fields = ['name']

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
                }
            }
            return Response(data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserRegisterView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
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
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

class UpdateUserInfoView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):
        serializer = UserSerializer(request.user, data=request.data, partial=True)
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
                return Response({'error': 'User is already a member of this bookclub'},
                                status=status.HTTP_400_BAD_REQUEST)

            Membership.objects.create(member=member, book_club=book_club)
            return Response({"detail": "Membership request submitted."}, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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
