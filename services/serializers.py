from django.contrib.auth import authenticate
from rest_framework import serializers
from django_filters import rest_framework as filters

from .models import Author, Book, BookCopy, Category, Order, OrderDetail, Publisher, User, BookClub, Member, \
    MembershipOrderDetail, Membership


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


class BookSerializer(serializers.ModelSerializer):
    category = CategorySerializer()
    author = AuthorSerializer()
    publisher = PublisherSerializer()

    class Meta:
        model = Book
        fields = ['name', 'category', 'author', 'publisher']


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


class UserSerializer(serializers.ModelSerializer):
    number_phone = serializers.CharField(allow_null=False)
    email = serializers.CharField(allow_null=False)
    location = serializers.CharField(allow_null=False)

    def update(self, instance, validated_data):
        # Update only the specified fields
        instance.email = validated_data.get('email', instance.email)
        instance.number_phone = validated_data.get('number_phone', instance.number_phone)
        instance.location = validated_data.get('location', instance.location)
        instance.save()
        return instance

    class Meta:
        model = User
        fields = ['username', 'password', 'number_phone', 'email', 'location']


class BookCopySerializer(serializers.ModelSerializer):
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
