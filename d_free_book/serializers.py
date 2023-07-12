from rest_framework import serializers

from services.serializers import ListIntegerField

class ClubBookGetIdsSerializer(serializers.Serializer):
    club_id = serializers.IntegerField()
    book_name = serializers.CharField(required=False)
    book_category_ids = ListIntegerField(required=False)
    book_author_ids = ListIntegerField(required=False)

class ClubBookGetInfosSerializer(serializers.Serializer):
    club_book_ids = ListIntegerField()

class GetOrderIdsSerializer(serializers.Serializer):
    club_id = serializers.IntegerField()
    from_date = serializers.DateField(required=False)
    to_date = serializers.DateField(required=False)

class ClubBookAddSerializer(serializers.Serializer):
    name = serializers.CharField()
    category_id = serializers.IntegerField()
    author = serializers.CharField()
    image = serializers.ImageField(required=False)
    init_count = serializers.IntegerField(default=1)
    current_count = serializers.IntegerField(default=1)
