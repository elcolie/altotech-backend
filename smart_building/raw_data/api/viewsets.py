from django.db.models import QuerySet
from rest_framework.viewsets import GenericViewSet, mixins

from raw_data.api.serializers import RawDataSerializer
from raw_data.models import RawData


class AbstractIoTViewSets(mixins.ListModelMixin, GenericViewSet):
    queryset = RawData.objects.all()
    serializer_class = RawDataSerializer


class IoTViewSets(AbstractIoTViewSets):
    def get_queryset(self) -> QuerySet[RawData]:
        room_id = self.kwargs.get('room_id')
        return RawData.objects.filter(device_id=room_id)


class LifeBeingViewSets(AbstractIoTViewSets):
    def get_queryset(self) -> QuerySet[RawData]:
        room_id = self.kwargs.get('room_id')
        return RawData.objects.filter(
            device_id=room_id,
            datapoint__in=["online_status", "sensitivity", "presence_state"]).order_by("-id")

class IAQViewSets(AbstractIoTViewSets):
    def get_queryset(self) -> QuerySet[RawData]:
        room_id = self.kwargs.get('room_id')
        return RawData.objects.filter(
            device_id=room_id,
            datapoint__in=["co2", "humidity", "temperature"]).order_by("-id")
