# Generated by Django 3.2.15 on 2023-05-31 13:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0044_alter_orderitem_price'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('Raw', 'Необработан'), ('Assembly', 'Сборка'), ('Delivery', 'Доставка'), ('Completed', 'Выполнен')], db_index=True, default='Принят', max_length=9, verbose_name='Статус заказа'),
        ),
    ]
