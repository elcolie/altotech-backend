from rest_framework import viewsets
from rest_framework import generics, mixins
from rest_framework.viewsets import GenericViewSet

from hotels.api.serializers import HotelSerializer, HotelFloorSerializer
from hotels.models import Hotel, HotelFloor
from rest_framework import filters

class HotelViewSets(
    mixins.ListModelMixin,
    GenericViewSet
):
    serializer_class = HotelSerializer
    queryset = Hotel.objects.all()
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', ]

class FloorViewSet(mixins.ListModelMixin, GenericViewSet):
    serializer_class = HotelFloorSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['floor_name', 'floor_number']

    def get_queryset(self):
        hotel_id = self.kwargs.get('hotel_id')
        return HotelFloor.objects.filter(hotel_id=hotel_id)
