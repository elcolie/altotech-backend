from rest_framework import serializers

from hotels.models import Hotel


class HotelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hotel
        fields = [
            "name",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]
