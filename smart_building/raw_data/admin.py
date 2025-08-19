from django.contrib import admin
from .models import RawData

# Register your models here.

@admin.register(RawData)
class RawDataAdmin(admin.ModelAdmin):
    list_display = ('device_id', 'datapoint', 'value', 'datetime', 'timestamp')
    list_filter = ('device_id', 'datapoint', 'datetime')
    search_fields = ('device_id', 'datapoint', 'value')
    ordering = ('-datetime',)
    readonly_fields = ('timestamp', 'datetime')
    list_per_page = 50

    fieldsets = (
        ('Device Information', {
            'fields': ('device_id', 'datapoint')
        }),
        ('Data', {
            'fields': ('value',)
        }),
        ('Timestamps', {
            'fields': ('datetime', 'timestamp'),
            'classes': ('collapse',)
        }),
    )
