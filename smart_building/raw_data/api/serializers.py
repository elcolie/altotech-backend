from rest_framework import serializers

from raw_data.models import RawData


class RawDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = RawData
        fields = [
            "timestamp",
            "datetime",
            "device_id",
            "datapoint",
            "value",
        ]
        read_only_fields = ["timestamp", "datetime"]
