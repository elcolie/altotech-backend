import random
from django.core.management.base import BaseCommand
from hotels.models import Hotel

try:
    from hotels.models import HotelFloor, Room
except ImportError:
    HotelFloor = None
    Room = None

from faker import Faker
fake = Faker()

class Command(BaseCommand):
    help = "Generate 10 fake hotels, each with 5-20 floors, each floor with ~30 rooms."

    def handle(self, *args, **options):
        hotel_names = set()
        while len(hotel_names) < 10:
            hotel_names.add(fake.company() + ' ' + fake.city())
        for hotel_name in hotel_names:
            hotel, _ = Hotel.objects.get_or_create(name=hotel_name)
            num_floors = random.randint(5, 20)
            self.stdout.write(f"Creating {hotel_name} with {num_floors} floors...")
            for floor_num in range(1, num_floors + 1):
                if HotelFloor:
                    floor, _ = HotelFloor.objects.get_or_create(hotel=hotel, floor_number=floor_num)
                else:
                    floor = None
                num_rooms = random.randint(28, 32)
                for room_num in range(1, num_rooms + 1):
                    room_name = f"{hotel_name}-F{floor_num}-R{room_num:03d}"
                    if Room and floor:
                        Room.objects.get_or_create(hotel=hotel, floor=floor, room_number=room_num, room_name=room_name)
                    elif Room:
                        Room.objects.get_or_create(hotel=hotel, room_number=room_num, room_name=room_name)
        self.stdout.write(self.style.SUCCESS("Fake hotels, floors, and rooms created!"))
