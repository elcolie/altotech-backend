from django.conf import settings
from rest_framework.routers import DefaultRouter
from rest_framework.routers import SimpleRouter
from django.urls import path, include

from hotels.api.viewsets import HotelViewSets, FloorViewSet

router = DefaultRouter() if settings.DEBUG else SimpleRouter()

router.register("hotels", HotelViewSets, basename="hotels")

app_name = "api"
urlpatterns = [
    path("", include(router.urls)),
    path("hotels/<int:hotel_id>/floors/", FloorViewSet.as_view({"get": "list"}), name="hotel-floors-list"),
]
