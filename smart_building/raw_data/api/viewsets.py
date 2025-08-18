from django.db.models import Avg, Sum, QuerySet, FloatField
from django.db.models.functions import Cast
from django.utils.dateparse import parse_datetime
from django.http import JsonResponse, HttpResponse
from rest_framework.decorators import api_view
from rest_framework.viewsets import GenericViewSet, mixins
import csv

from raw_data.api.serializers import RawDataSerializer
from raw_data.models import RawData
import datetime

SUBSYSTEM_METERS = {
    'ac': ['power_meter_1', 'power_meter_2', 'power_meter_3'],
    'lighting': ['power_meter_4', 'power_meter_5'],
    'plug_load': ['power_meter_6'],
}
ALL_METERS = SUBSYSTEM_METERS['ac'] + SUBSYSTEM_METERS['lighting'] + SUBSYSTEM_METERS['plug_load']


class AbstractIoTViewSets(mixins.ListModelMixin, GenericViewSet):
    queryset = RawData.objects.all()
    serializer_class = RawDataSerializer


class IoTViewSets(AbstractIoTViewSets):
    def get_queryset(self) -> QuerySet[RawData]:
        room_id = self.kwargs.get('room_id')
        return RawData.objects.filter(device_id=room_id)


class LifeBeingViewSets(AbstractIoTViewSets):
    def get_queryset(self) -> QuerySet[RawData]:
        room_id = self.kwargs.get('room_id')
        return RawData.objects.filter(
            device_id=room_id,
            datapoint__in=["online_status", "sensitivity", "presence_state"]).order_by("-id")

class IAQViewSets(AbstractIoTViewSets):
    def get_queryset(self) -> QuerySet[RawData]:
        room_id = self.kwargs.get('room_id')
        return RawData.objects.filter(
            device_id=room_id,
            datapoint__in=["co2", "humidity", "temperature"]).order_by("-id")


@api_view(['GET'])
def energy_summary(request, hotel_id):
    resolution = request.GET.get('resolution')
    subsystem = request.GET.get('subsystem')
    start_time = request.GET.get('start_time')
    end_time = request.GET.get('end_time')
    as_csv = request.GET.get('file_format') == 'csv'

    if resolution not in ['1hour', '1day', '1month']:
        return JsonResponse({'error': 'resolution must be one of [1hour, 1day, 1month]'}, status=400)

    # Subsystem filter
    if subsystem:
        meters = SUBSYSTEM_METERS.get(subsystem)
        if not meters:
            return JsonResponse({'error': f'Invalid subsystem: {subsystem}'}, status=400)
        subsystems = [subsystem]
    else:
        meters = ALL_METERS
        subsystems = list(SUBSYSTEM_METERS.keys())

    # Date range filter
    try:
        if start_time:
            start_dt = parse_datetime(start_time)
        else:
            start_dt = None
        if end_time:
            end_dt = parse_datetime(end_time)
        else:
            end_dt = None
    except Exception:
        return JsonResponse({'error': 'Invalid date format for start_time or end_time'}, status=400)

    # Build queryset
    qs = RawData.objects.filter(device_id__in=meters, datapoint='power_kw')
    if start_dt:
        qs = qs.filter(datetime__gte=start_dt)
    if end_dt:
        qs = qs.filter(datetime__lte=end_dt)
    qs = qs.annotate(value_float=Cast('value', FloatField()))

    # Resolution grouping
    if resolution == '1hour':
        trunc = 'hour'
        fmt = '%Y-%m-%d %H:00:00'
    elif resolution == '1day':
        trunc = 'day'
        fmt = '%Y-%m-%d'
    elif resolution == '1month':
        trunc = 'month'
        fmt = '%Y-%m'

    # Annotate and aggregate
    from django.db.models.functions import TruncHour, TruncDay, TruncMonth
    if trunc == 'hour':
        qs = qs.annotate(period=TruncHour('datetime'))
    elif trunc == 'day':
        qs = qs.annotate(period=TruncDay('datetime'))
    elif trunc == 'month':
        qs = qs.annotate(period=TruncMonth('datetime'))

    # Calculate average power per period per subsystem
    summary = {}
    for subsystem_name, subsystem_meters in SUBSYSTEM_METERS.items():
        if subsystem and subsystem_name != subsystem:
            continue
        subsystem_qs = qs.filter(device_id__in=subsystem_meters)
        periods = subsystem_qs.values('period').annotate(avg_kw=Avg('value_float'), runhour=Sum(1)).order_by('period')
        for p in periods:
            key = int(p['period'].timestamp())
            if key not in summary:
                summary[key] = {s: 0.0 for s in subsystems}
                summary[key]['timestamp'] = key
            avg_kw = float(p['avg_kw']) if p['avg_kw'] is not None else 0.0
            runhour = p['runhour'] if p['runhour'] else 0
            summary[key][subsystem_name] += avg_kw * runhour
    # Return as sorted list
    result = sorted(summary.values(), key=lambda x: x['timestamp'])

    if as_csv:
        # CSV response
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=energy_summary.csv'
        writer = csv.writer(response)
        header = ['timestamp'] + subsystems
        writer.writerow(header)
        for row in result:
            writer.writerow([row['timestamp']] + [row[s] for s in subsystems])
        return response
    else:
        return JsonResponse(result, safe=False)
