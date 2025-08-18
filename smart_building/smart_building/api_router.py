from django.conf import settings
from rest_framework.routers import DefaultRouter
from rest_framework.routers import SimpleRouter

from hotels.api.viewsets import HotelViewSets

router = DefaultRouter() if settings.DEBUG else SimpleRouter()

router.register("hotels", HotelViewSets, basename="hotels")

app_name = "api"
urlpatterns = router.urls
