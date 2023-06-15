from django.contrib.auth import authenticate
from rest_framework import serializers

from .models import Author, Book, BookCopy, Category, Order, OrderDetail, Publisher, User


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
