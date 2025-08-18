from django.db import models


class RawData(models.Model):
    timestamp = models.BigIntegerField()
    datetime = models.DateTimeField()
    device_id = models.TextField(db_index=True)
    datapoint = models.TextField()
    value = models.TextField()

    class Meta:
        indexes = [
            models.Index(fields=['device_id'])
        ]

    def __str__(self):
        return f"{self.device_id} | {self.datapoint} | {self.value} @ {self.datetime}"
