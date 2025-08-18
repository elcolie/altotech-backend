from django.db import models


class Hotel(models.Model):
    name = models.CharField(max_length=255, unique=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"{self.name}"


class HotelFloor(models.Model):
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name='floors')
    floor_number = models.IntegerField()
    floor_name = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self) -> str:
        return f"{self.hotel.name} | {self.floor_number}"


class Room(models.Model):
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name='rooms')
    floor = models.ForeignKey(HotelFloor, on_delete=models.CASCADE, related_name='rooms')
    room_number = models.IntegerField()
    room_name = models.CharField(max_length=255, null=True, blank=True)
    iaq_sensor = models.CharField(max_length=255, null=True, blank=True)
    life_being_sensor = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self) -> str:
        return f"{self.hotel.name} | {self.floor.floor_number} | {self.room_number}"
