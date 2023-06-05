from rest_framework import serializers
from .models import Book, User, OrderDetail, BookCopy
from .models import Order


class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = '__all__'  # Include all fields in the serialization


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
    class Meta:
        model = User
        fields = '__all__'


class BookCopySerializer(serializers.ModelSerializer):
    class Meta:
        model = BookCopy
        fields = '__all__'
