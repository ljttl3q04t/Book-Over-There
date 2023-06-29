from datetime import timedelta, datetime

from django.contrib.auth import authenticate
from django.utils import timezone
from rest_framework import serializers
from django_filters import rest_framework as filters

from .models import Author, Book, BookCopy, Category, Order, OrderDetail, Publisher, User, BookClub, Member, \
    MembershipOrderDetail, Membership, MemberBookCopy


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
    def to_representation(self, instance):
        data = super().to_representation(instance)
        avatar = instance.avatar
        if avatar:
            data['avatar'] = avatar.url.split('?')[0]
        return data

    class Meta:
        model = User
        fields = ['phone_number', 'email', 'address', 'full_name', 'birth_date', 'avatar', 'username']


class BookSerializer(serializers.ModelSerializer):
    category = CategorySerializer()
    author = AuthorSerializer()
    publisher = PublisherSerializer()

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

    def to_representation(self, instance):
        data = super().to_representation(instance)
        book_image = instance.image.name
        if 'fahasa.com' in book_image:
            data['image'] = book_image
        else:
            data['image'] = instance.image.url.split('?')[0] if instance.image else ''

        return data

    class Meta:
        model = Book
        fields = ['name', 'category', 'author', 'publisher', 'image']


class BookFilter(filters.FilterSet):
    category = filters.CharFilter(field_name='category__name', lookup_expr='icontains')
    publisher = filters.CharFilter(field_name='publisher__name', lookup_expr='icontains')
    author = filters.CharFilter(field_name='author__name', lookup_expr='icontains')

    class Meta:
        model = Book
        fields = ['category', 'publisher', 'author']


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
    is_member = serializers.BooleanField(default=False)

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


class MembershipOrderDetailSerializer(serializers.ModelSerializer):
    def validate_member_book_copy(self, member_book_copy):
        if member_book_copy.current_reader is not None:
            raise serializers.ValidationError("The book copy is currently assigned to a reader.")
        return member_book_copy

    class Meta:
        model = MembershipOrderDetail
        fields = ['member_book_copy', 'due_date']


class MembershipOrderSerializer(serializers.Serializer):
    membership_id = serializers.IntegerField(required=True)
    order_details = MembershipOrderDetailSerializer(required=True, many=True)

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
        if not data.get('book_id'):
            if not data.get('book'):
                raise serializers.ValidationError("Missing field required")
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
    member_book_copy_id = serializers.IntegerField(required=True)
    description = serializers.CharField(max_length=200, required=False)
    attachment = serializers.FileField(required=False)

    def validate(self, data):
        member_book_copy_id = data.get('member_book_copy_id')
        record = MemberBookCopy.objects.filter(id=member_book_copy_id).first()
        if not record:
            raise serializers.ValidationError("Member book copy not found")
        if record.current_reader:
            raise serializers.ValidationError("Book is borrowing")
        if record.onboard_date:
            raise serializers.ValidationError("Book already in club")
        return record


class BookClubMemberWithdrawBookSerializer(serializers.Serializer):
    member_book_copy_id = serializers.IntegerField(required=True)
    description = serializers.CharField(max_length=200, required=False)
    attachment = serializers.FileField(required=False)

    def validate(self, data):
        member_book_copy_id = data.get('member_book_copy_id')
        record = MemberBookCopy.objects.filter(id=member_book_copy_id, is_enabled=True).first()
        if not record:
            raise serializers.ValidationError("Member book copy not found")
        if record.current_reader:
            raise serializers.ValidationError("Book is borrowing")
        if not record.onboard_date:
            raise serializers.ValidationError("Book not in club")

        onboard_datetime = datetime.combine(record.onboard_date, datetime.min.time())
        delta = datetime.now() - onboard_datetime
        if delta.days <= 30:
            raise serializers.ValidationError("Book onboard date not exceeded 30 days")
        return record


class BookClubStaffCreateOrderSerializer(serializers.Serializer):
    membership_id = serializers.IntegerField()
    member_book_copy_ids = serializers.ListSerializer(child=serializers.IntegerField())
    due_date = serializers.DateTimeField()

    def validate(self, data):
        membership = Membership.objects.filter(id=data['membership_id']).first()
        if not membership:
            raise serializers.ValidationError('membership not found')
        member_book_copys = MemberBookCopy.objects.filter(
            id__in=data['member_book_copy_ids'],
            current_reader=None,
            onboard_date__isnull=False,
            is_enabled=True,
        )
        if len(member_book_copys) != len(data['member_book_copy_ids']):
            raise serializers.ValidationError('invalid books')
        return membership, member_book_copys


class MemberBookCopySerializer(serializers.ModelSerializer):
    membership = MembershipSerializer()
    book_copy = BookCopySerializer()
    current_reader = MembershipSerializer()

    class Meta:
        model = MemberBookCopy
        fields = '__all__'
