from rest_framework import viewsets
from rest_framework import generics, mixins
from rest_framework.viewsets import GenericViewSet

from hotels.api.serializers import HotelSerializer
from hotels.models import Hotel
from rest_framework import filters

class HotelViewSets(
    mixins.ListModelMixin,
    GenericViewSet
):
    serializer_class = HotelSerializer
    queryset = Hotel.objects.all()
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', ]
