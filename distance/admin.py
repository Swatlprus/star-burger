from django.contrib import admin
from .models import Place


@admin.register(Place)
class DistanceAdmin(admin.ModelAdmin):
    list_display = [
        'address',
        'updated_time',
    ]
