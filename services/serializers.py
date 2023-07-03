from datetime import datetime

from django.contrib.auth import authenticate
from django_filters import rest_framework as filters
from rest_framework import serializers

from .models import Author, Book, BookCopy, Category, Order, OrderDetail, Publisher, User, BookClub, Member, \
    MembershipOrderDetail, Membership, MemberBookCopy, MembershipOrder, BookCopyHistory

class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):
        username = data.get('username')
        password = data.get('password')

        if username and password:
            user = authenticate(username=username, password=password)

            if not user:
                raise serializers.ValidationError('Invalid username or password.')

        else:
            raise serializers.ValidationError('Please provide both username and password.')

        data['user'] = user
        return data

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['name']

class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = ['name']

class PublisherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Publisher
        fields = ['name']

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['phone_number', 'email', 'address', 'full_name', 'birth_date', 'avatar', 'username']

class BookSerializer(serializers.ModelSerializer):
    category = CategorySerializer()
    author = AuthorSerializer()
    publisher = PublisherSerializer()
    image = serializers.ImageField(required=False)
    image_url = serializers.CharField(required=False)

    def create(self, validated_data):
        category, _ = Category.objects.get_or_create(name=validated_data.get('category').get('name'))
        author, _ = Author.objects.get_or_create(name=validated_data.get('author').get('name'))
        publisher, _ = Publisher.objects.get_or_create(name=validated_data.get('publisher').get('name'))
        return Book.objects.create(
            name=validated_data['name'],
            category=category,
            author=author,
            publisher=publisher,
            image=validated_data.get('image'),
        )

    class Meta:
        model = Book
        fields = ['name', 'category', 'author', 'publisher', 'image', 'image_url']

class BookFilter(filters.FilterSet):
    category = filters.CharFilter(field_name='category__name', lookup_expr='icontains')
    publisher = filters.CharFilter(field_name='publisher__name', lookup_expr='icontains')
    author = filters.CharFilter(field_name='author__name', lookup_expr='icontains')

    class Meta:
        model = Book
        fields = ['category', 'publisher', 'author']

class ClubBookListFilter(filters.FilterSet):
    membership_id = filters.NumberFilter(field_name='membership__id', lookup_expr='exact')
    book_copy__book_status = filters.ChoiceFilter(choices=BookCopy.BOOK_STATUS_CHOICES)
    deposit_book = filters.BooleanFilter(method='filter_deposit_book')
    withdraw_book = filters.BooleanFilter(method='filter_withdraw_book')
    create_order_book = filters.BooleanFilter(method='filter_create_order_book')

    def filter_deposit_book(self, queryset, _, value):
        if value:
            return queryset.filter(current_reader__isnull=True, onboard_date__isnull=True)
        else:
            return queryset

    def filter_withdraw_book(self, queryset, _, value):
        if value:
            return queryset \
                .filter(book_copy__book_status=BookCopy.SHARING_CLUB, current_reader__isnull=True)
        else:
            return queryset

    def filter_create_order_book(self, queryset, _, value):
        if value:
            return queryset \
                .filter(book_copy__book_status=BookCopy.SHARING_CLUB, current_reader__isnull=True,
                        onboard_date__isnull=False, is_enabled=True)
        else:
            return queryset

    class Meta:
        model = MemberBookCopy
        fields = ['membership_id', 'book_copy__book_status', 'deposit_book', 'withdraw_book', 'create_order_book']

class OrderDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderDetail
        fields = ['book_copy', 'due_date', 'return_date']

class OrderSerializer(serializers.ModelSerializer):
    order_details = OrderDetailSerializer(many=True)

    class Meta:
        model = Order
        fields = '__all__'

    def create(self, validated_data):
        order_details_data = validated_data.pop('order_details')
        order = Order.objects.create(**validated_data)
        for order_detail_data in order_details_data:
            order_detail_data['order'] = order
            OrderDetail.objects.create(**order_detail_data)
        return order

class GetOrderDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderDetail
        fields = ['id', 'book_copy', 'due_date', 'return_date']

class GetOrderSerializer(serializers.ModelSerializer):
    order_details = GetOrderDetailSerializer(many=True)

    class Meta:
        model = Order
        fields = ['id', 'order_user', 'order_date', 'total_book', 'comment', 'status', 'order_details']

class UserRegisterSerializer(serializers.ModelSerializer):
    phone_number = serializers.CharField(allow_null=False)
    email = serializers.CharField(allow_null=False)

    class Meta:
        model = User
        fields = ['username', 'password', 'phone_number', 'email']

class UserUpdateSerializer(serializers.ModelSerializer):
    phone_number = serializers.CharField(allow_null=False)
    email = serializers.CharField(allow_null=False)
    address = serializers.CharField(allow_null=False)
    full_name = serializers.CharField(allow_null=False)
    birth_date = serializers.DateField(allow_null=False)
    username = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = ['phone_number', 'email', 'address', 'full_name', 'birth_date', 'avatar', 'username']
        read_only_fields = ['username']

class BookCheckSerializer(serializers.Serializer):
    remote_url = serializers.CharField()

class BookCopySerializer(serializers.ModelSerializer):
    book = BookSerializer()

    class Meta:
        model = BookCopy
        fields = '__all__'

class MemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = Member
        fields = '__all__'

class BookClubSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookClub
        fields = '__all__'

class BookClubRequestToJoinSerializer(serializers.Serializer):
    club_id = serializers.IntegerField()
    full_name = serializers.CharField()
    birth_date = serializers.DateField()
    email = serializers.EmailField()
    phone_number = serializers.CharField()
    address = serializers.CharField()

class MembershipOrderDetailCreateSerializer(serializers.ModelSerializer):
    def validate_member_book_copy(self, member_book_copy):
        if member_book_copy.current_reader is not None:
            raise serializers.ValidationError("The book copy is currently assigned to a reader.")
        return member_book_copy

    class Meta:
        model = MembershipOrderDetail
        fields = ['member_book_copy', 'due_date']

class MembershipOrderCreateSerializer(serializers.Serializer):
    membership_id = serializers.IntegerField(required=True)
    order_details = MembershipOrderDetailCreateSerializer(required=True, many=True)

    def validate(self, data):
        membership_id = data.get('membership_id')
        membership = Membership.objects.get(id=membership_id)

        if membership.leaved_at is not None:
            raise serializers.ValidationError("The membership has already ended.")

        return data

class MembershipSerializer(serializers.ModelSerializer):
    member = MemberSerializer()
    book_club = BookClubSerializer()

    class Meta:
        model = Membership
        fields = '__all__'

class MyBookAddSerializer(serializers.Serializer):
    book_id = serializers.IntegerField(required=False)
    book = BookSerializer(required=False)

    def validate(self, data):
        data = super().validate(data)
        if not data.get('book_id'):
            if not data.get('book'):
                raise serializers.ValidationError("Missing field book_id or book")
        return data

class ShareBookClubSerializer(serializers.Serializer):
    book_copy_ids = serializers.ListSerializer(child=serializers.IntegerField())
    club_id = serializers.IntegerField()

    def validate(self, data):
        club = BookClub.objects.filter(id=data['club_id']).first()
        if not club:
            raise serializers.ValidationError("Club not found")

        request_user = self.context['request'].user
        membership = Membership.objects.filter(member__user=request_user, book_club=club).first()
        if not membership:
            raise serializers.ValidationError("membership not found")

        books = BookCopy.objects \
            .filter(user=request_user, id__in=data['book_copy_ids'], book_status=BookCopy.NEW).all()
        if len(books) != len(data['book_copy_ids']):
            raise serializers.ValidationError("Book not found or invalid book_status")

        return membership, books

class BookClubMemberUpdateSerializer(serializers.Serializer):
    membership_id = serializers.IntegerField()
    member_status = serializers.ChoiceField(choices=Membership.MEMBER_STATUS_CHOICES)

class BookClubMemberDepositBookSerializer(serializers.Serializer):
    member_book_copy_ids = serializers.CharField()
    description = serializers.CharField(max_length=200, required=False)
    attachment = serializers.FileField(required=False)

    def validate(self, data):
        try:
            member_book_copy_ids = [int(i) for i in data['member_book_copy_ids'].split(',')]
        except:
            raise serializers.ValidationError('invalid member_book_copy_ids')
        member_book_copys = MemberBookCopy.objects \
            .filter(id__in=member_book_copy_ids, current_reader__isnull=True, onboard_date__isnull=True)
        if len(member_book_copys) != len(member_book_copy_ids):
            raise serializers.ValidationError('invalid member_book_copy_ids')

        return member_book_copys

class BookClubMemberWithdrawBookSerializer(serializers.Serializer):
    member_book_copy_ids = serializers.CharField()
    description = serializers.CharField(max_length=200, required=False)
    attachment = serializers.FileField(required=False)

    def validate(self, data):
        try:
            member_book_copy_ids = [int(i) for i in data['member_book_copy_ids'].split(',')]
        except:
            raise serializers.ValidationError('invalid member_book_copy_ids')

        member_book_copys = MemberBookCopy.objects.filter(id__in=member_book_copy_ids)

        if len(member_book_copys) != len(member_book_copy_ids):
            raise serializers.ValidationError("Member book copy not found")
        for r in member_book_copys:
            if r.current_reader:
                raise serializers.ValidationError("Book is borrowing")
            if not r.onboard_date:
                raise serializers.ValidationError("Book not in club")

        # onboard_datetime = datetime.combine(record.onboard_date, datetime.min.time())
        # delta = datetime.now() - onboard_datetime
        # if delta.days <= 30:
        #     raise serializers.ValidationError("Book onboard date not exceeded 30 days")
        return member_book_copys

class BookClubStaffExtendOrderSerializer(serializers.Serializer):
    membership_order_detail_ids = serializers.CharField()
    new_due_date = serializers.DateTimeField()
    note = serializers.CharField(max_length=500)
    attachment = serializers.FileField(required=False)

    def validate(self, data):
        try:
            membership_order_detail_ids = [int(i) for i in data['membership_order_detail_ids'].split(',')]
        except:
            raise serializers.ValidationError('invalid membership_order_detail_ids')

        order_details = MembershipOrderDetail.objects.filter(id__in=membership_order_detail_ids)
        if len(order_details) != len(membership_order_detail_ids):
            raise serializers.ValidationError('membership_order_detail_ids missmatch')

        membership_borrower = order_details[0].order.membership
        book_copy_ids = [order_detail.member_book_copy.book_copy_id for order_detail in order_details]
        return order_details, membership_borrower, book_copy_ids

class BookClubStaffCreateOrderSerializer(serializers.Serializer):
    membership_id = serializers.IntegerField()
    member_book_copy_ids = serializers.CharField()
    due_date = serializers.DateTimeField()
    note = serializers.CharField(max_length=500)
    attachment = serializers.FileField(required=False)

    def validate(self, data):
        try:
            member_book_copy_ids = [int(i) for i in data['member_book_copy_ids'].split(',')]
        except:
            raise serializers.ValidationError('invalid member_book_copy_ids')

        membership = Membership.objects.filter(id=data['membership_id']).first()
        if not membership:
            raise serializers.ValidationError('membership not found')
        member_book_copys = MemberBookCopy.objects.filter(
            id__in=member_book_copy_ids,
            current_reader=None,
            onboard_date__isnull=False,
            is_enabled=True,
        )
        if len(member_book_copys) != len(member_book_copy_ids):
            raise serializers.ValidationError('invalid books')
        return membership, member_book_copys

# class ReturnBookSerializer(serializers.Serializer):

class UserBorrowingBookSerializer(serializers.ModelSerializer):

    def to_representation(self, instance):
        book = instance.member_book_copy.book_copy.book
        book_image = book.image.url if book.image else ''
        return {
            'order_detail_id': instance.id,
            'order_id': instance.order.id,
            'book_name': book.name,
            'book_image': book_image,
            'start_date': instance.order.confirm_date,
            'due_date': instance.due_date,
            'overdue_day_count': instance.overdue_day_count,
            'club_name': instance.order.membership.book_club.name,
        }

    class Meta:
        model = MembershipOrderDetail
        fields = ['order', 'member_book_copy', 'due_date', 'overdue_day_count']

class MemberBookCopySerializer(serializers.ModelSerializer):
    membership = MembershipSerializer()
    book_copy = BookCopySerializer()
    current_reader = MembershipSerializer()

    class Meta:
        model = MemberBookCopy
        fields = '__all__'

class StaffBorrowingSerializer(serializers.Serializer):
    membership_id = serializers.IntegerField()

    def validate(self, data):
        membership = Membership.objects.filter(id=data['membership_id']).first()
        if not membership:
            raise serializers.ValidationError('membership_id not found')
        return membership

class BookCopyHistorySerializer(serializers.ModelSerializer):
    book_copy = BookCopySerializer()
    membership_borrower = MembershipSerializer()
    attachment = serializers.FileField(source='attachment.file', read_only=True)

    class Meta:
        model = BookCopyHistory
        fields = '__all__'
