from rest_framework import serializers

from hotels.models import Hotel, HotelFloor, Room


class HotelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hotel
        fields = [
            "name",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]

class HotelFloorSerializer(serializers.ModelSerializer):
    class Meta:
        model = HotelFloor
        fields = [
            "hotel",
            "floor_number",
            "floor_name",
        ]

class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = [
            "hotel",
            "floor",
            "room_number",
            "room_name",
        ]
