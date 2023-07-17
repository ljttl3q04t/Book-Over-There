from rest_framework import serializers

from services.serializers import ListIntegerField

class ClubBookGetIdsSerializer(serializers.Serializer):
    club_id = serializers.IntegerField(required=False)
    club_ids = ListIntegerField(required=False)
    book_name = serializers.CharField(required=False)
    book_category_ids = ListIntegerField(required=False)
    book_author_ids = ListIntegerField(required=False)

class ClubBookGetInfosSerializer(serializers.Serializer):
    club_book_ids = ListIntegerField()

class GetOrderIdsSerializer(serializers.Serializer):
    club_id = serializers.IntegerField(required=False)
    from_date = serializers.DateField(required=False)
    to_date = serializers.DateField(required=False)

class GetOrderInfosSerializer(serializers.Serializer):
    order_ids = ListIntegerField()

class ClubBookAddSerializer(serializers.Serializer):
    club_id = serializers.IntegerField()
    name = serializers.CharField()
    code = serializers.CharField()
    category = serializers.CharField()
    author = serializers.CharField()
    image = serializers.ImageField(required=False)
    init_count = serializers.IntegerField(default=1)
    current_count = serializers.IntegerField(default=1)

class ClubBookUpdateSerializer(serializers.Serializer):
    club_book_id = serializers.IntegerField()
    code = serializers.CharField(required=False)
    init_count = serializers.IntegerField(required=False)
    current_count = serializers.IntegerField(required=False)

class OrderDetailGetIdsSerializer(serializers.Serializer):
    club_id = serializers.IntegerField(required=False)
    from_date = serializers.DateField(required=False)
    to_date = serializers.DateField(required=False)

class OrderDetailGetInfosSerializer(serializers.Serializer):
    order_detail_ids = ListIntegerField()

class OrderCreateSerializer(serializers.Serializer):
    member_full_name = serializers.CharField()
    member_code = serializers.CharField()
    member_phone_number = serializers.CharField()
    order_date = serializers.DateField()
    due_date = serializers.DateField()
    club_id = serializers.IntegerField()
    note = serializers.CharField(required=False)
    book_note = serializers.CharField(required=False)
    club_book_ids = ListIntegerField(required=False)
    book_notes = serializers.ListSerializer(child=serializers.CharField(), required=False)

class MemberGetIdsSerializer(serializers.Serializer):
    code = serializers.CharField(required=False)
    phone_number = serializers.CharField(required=False)
    full_name = serializers.CharField(required=False)

class MemberGetInfosSerializer(serializers.Serializer):
    member_ids = ListIntegerField()

class MemberCreateSerializer(serializers.Serializer):
    club_id = serializers.IntegerField()
    code = serializers.CharField()
    phone_number = serializers.CharField(required=False)
    full_name = serializers.CharField()

class MemberUpdateSerializer(serializers.Serializer):
    member_id = serializers.IntegerField()
    code = serializers.CharField(required=False)
    phone_number = serializers.CharField(required=False)
    full_name = serializers.CharField(required=False)
