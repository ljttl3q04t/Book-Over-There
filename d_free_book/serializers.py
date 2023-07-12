from rest_framework import serializers

class ClubBookGetIdsSerializer(serializers.Serializer):
    club_id = serializers.IntegerField()

class ClubBookGetInfosSerializer(serializers.Serializer):
    club_book_ids = serializers.ListSerializer(child=serializers.IntegerField)
