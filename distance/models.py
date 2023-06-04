from django.db import models
from django.utils import timezone


class Place(models.Model):
    address = models.CharField(
        verbose_name='Адрес',
        max_length=150,
        unique=True,
    )
    lat = models.DecimalField(
        verbose_name='Широта',
        decimal_places=2,
        max_digits=9,
        blank=True,
        null=True,
    )
    lon = models.DecimalField(
        verbose_name='Долгота',
        decimal_places=2,
        max_digits=9,
        blank=True,
        null=True,
    )
    updated_time = models.DateTimeField(
        'Дата обновления',
        default=timezone.now
    )

    class Meta:
        verbose_name = 'Место'
        verbose_name_plural = 'Места'

    def __str__(self):
        return f'{self.address} {self.updated_time}'
