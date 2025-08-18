import csv
import os
from datetime import datetime

from django.core.management.base import BaseCommand

from raw_data.models import RawData


class Command(BaseCommand):
    help = "Import sample_power_meter_data.csv into RawData table as timeseries data."

    def handle(self, *args, **options):
        csv_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
            'raw_data',
            'management',
            'commands',
            'sample_power_meter_data.csv'
        )
        if not os.path.exists(csv_path):
            self.stdout.write(self.style.ERROR(f"CSV file not found: {csv_path}"))
            return
        with open(csv_path, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            rawdata_objs = []
            count = 0
            for row in reader:
                dt_str = row['datetime']
                try:
                    dt = datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S.%f")
                except ValueError:
                    dt = datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
                timestamp = int(dt.timestamp())
                for key in row:
                    if key == 'datetime':
                        continue
                    device_id = key.replace('power_kw_', '')  # e.g. power_meter_1
                    datapoint = 'power_kw'
                    value = row[key]
                    rawdata_objs.append(RawData(
                        timestamp=timestamp,
                        datetime=dt,
                        device_id=device_id,
                        datapoint=datapoint,
                        value=value
                    ))
                    count += 1
            RawData.objects.bulk_create(rawdata_objs)
            self.stdout.write(self.style.SUCCESS(f"Imported {count} power meter records into RawData table."))
