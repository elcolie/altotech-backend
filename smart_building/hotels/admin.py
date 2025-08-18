from django.contrib import admin
from .models import Hotel, HotelFloor, Room

class HotelAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "created_at", "updated_at")
    search_fields = ("name",)
    list_filter = ("created_at", "updated_at")

class FloorAdmin(admin.ModelAdmin):
    list_display = ("id", "hotel", "floor_number", "floor_name")
    search_fields = ("hotel__name", "floor_name")
    list_filter = ("hotel", "floor_number")

class RoomAdmin(admin.ModelAdmin):
    list_display = ("id", "hotel", "floor", "room_number", "room_name")
    search_fields = ("hotel__name", "room_name")
    list_filter = ("hotel", "floor", "room_number")

admin.site.register(Hotel, HotelAdmin)
admin.site.register(HotelFloor, FloorAdmin)
admin.site.register(Room, RoomAdmin)
