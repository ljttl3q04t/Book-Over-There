from rest_framework import serializers

from services.managers import membership_manager
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
    order_date = serializers.DateField(required=False)
    order_status = serializers.CharField(required=False)

class GetOrderInfosSerializer(serializers.Serializer):
    order_ids = ListIntegerField()

class GetDraftOrderInfosSerializer(serializers.Serializer):
    draft_order_ids = ListIntegerField()

class ClubBookAddSerializer(serializers.Serializer):
    club_id = serializers.IntegerField()
    name = serializers.CharField()
    code = serializers.CharField()
    category = serializers.CharField()
    author = serializers.CharField()
    image = serializers.ImageField(required=False)
    image_url = serializers.CharField(required=False)
    init_count = serializers.IntegerField(default=1)
    current_count = serializers.IntegerField(default=1)

class ClubBookUpdateSerializer(serializers.Serializer):
    club_book_id = serializers.IntegerField()
    code = serializers.CharField(required=False)
    init_count = serializers.IntegerField(required=False)
    current_count = serializers.IntegerField(required=False)

class OrderCreateSerializer(serializers.Serializer):
    member_id = serializers.IntegerField(required=False)
    order_date = serializers.DateField()
    due_date = serializers.DateField()
    club_id = serializers.IntegerField()
    note = serializers.CharField(required=False)
    club_book_ids = ListIntegerField(required=False)
    creator_order_id = serializers.IntegerField(required=False)

class DraftOrderCreateSerializer(serializers.Serializer):
    full_name = serializers.CharField()
    phone_number = serializers.CharField()
    address = serializers.CharField()
    order_date = serializers.DateField()
    due_date = serializers.DateField()
    club_book_ids = ListIntegerField()
    user_id = serializers.IntegerField()
    club_id = serializers.IntegerField()

class OrderReturnBooksSerializer(serializers.Serializer):
    order_detail_ids = ListIntegerField()
    return_date = serializers.DateField(required=False)
    receiver_id = serializers.IntegerField(required=False)

class MemberGetIdsSerializer(serializers.Serializer):
    code = serializers.CharField(required=False)
    phone_number = serializers.CharField(required=False)
    full_name = serializers.CharField(required=False)
    club_id = serializers.IntegerField(required=False)

class MemberGetInfosSerializer(serializers.Serializer):
    member_ids = ListIntegerField()

class MemberCreateSerializer(serializers.Serializer):
    code = serializers.CharField()
    phone_number = serializers.CharField(required=False)
    full_name = serializers.CharField()
    club_id = serializers.IntegerField()
    notes = serializers.CharField(max_length=500, required=False)

class MemberUpdateSerializer(serializers.Serializer):
    member_id = serializers.IntegerField()
    code = serializers.CharField(required=False)
    phone_number = serializers.CharField(required=False)
    full_name = serializers.CharField(required=False)
    notes = serializers.CharField(max_length=500, required=False, allow_blank=True)

class MemberCheckSerializer(serializers.Serializer):
    phone_number = serializers.CharField(required=True)
    club_id = serializers.IntegerField()

class OrderCreateNewMemberSerializer(serializers.Serializer):
    new_member = MemberCreateSerializer()
    order_date = serializers.DateField()
    due_date = serializers.DateField()
    note = serializers.CharField(required=False)
    club_book_ids = ListIntegerField(required=False)
    creator_order_id = serializers.IntegerField(required=False)

class OrderCreateFromDraftSerializer(serializers.Serializer):
    draft_id = serializers.IntegerField(required=True)
    member_id = serializers.IntegerField(required=False)
    order_date = serializers.DateField()
    due_date = serializers.DateField()
    club_id = serializers.IntegerField()
    address = serializers.CharField(required=True)
    club_book_ids = ListIntegerField(required=False)
    creator_order_id = serializers.IntegerField(required=False)

class OrderCreateFromDraftNewMemberSerializer(serializers.Serializer):
    draft_id = serializers.IntegerField(required=True)
    new_member = MemberCreateSerializer()
    order_date = serializers.DateField()
    due_date = serializers.DateField()
    address = serializers.CharField(required=True)
    club_book_ids = ListIntegerField(required=False)
    creator_order_id = serializers.IntegerField(required=False)

class DraftOrderUpdateSerializer(serializers.Serializer):
    draft_order_id = serializers.IntegerField()
    club_id = serializers.IntegerField()
    order_date = serializers.DateField(required=False)
    due_date = serializers.DateField(required=False)
    phone_number = serializers.CharField(required=False)
    full_name = serializers.CharField(required=False)
    club_books = serializers.CharField(required=False)
    address = serializers.CharField(required=False)
