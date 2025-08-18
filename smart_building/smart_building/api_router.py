from django.conf import settings
from rest_framework.routers import DefaultRouter
from rest_framework.routers import SimpleRouter
from django.urls import path, include

from hotels.api.viewsets import HotelViewSets
from hotels.api.viewsets import FloorViewSet, RoomViewSet
from raw_data.api.viewsets import IoTViewSets, LifeBeingViewSets, IAQViewSets

router = DefaultRouter() if settings.DEBUG else SimpleRouter()

router.register("hotels", HotelViewSets, basename="hotels")

app_name = "api"
urlpatterns = [
    path("", include(router.urls)),
    path("hotels/<int:hotel_id>/floors/", FloorViewSet.as_view({"get": "list"}), name="hotel-floors-list"),
    path("floors/<int:floor_id>/rooms/", RoomViewSet.as_view({"get": "list"}), name="floor-rooms-list"),
    path("rooms/<int:room_id>/data/", IoTViewSets.as_view({"get": "list"}), name="room-iot-list"),
    path("rooms/<int:room_id>/data/life_being/", LifeBeingViewSets.as_view({"get": "list"}), name="room-iot-list"),
    path("rooms/<int:room_id>/data/iaq/", IAQViewSets.as_view({"get": "list"}), name="room-iot-list"),
]
