# Generated by Django 3.2.15 on 2023-06-01 06:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0047_auto_20230601_0548'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='payment',
            field=models.CharField(choices=[('Cash', 'Наличностью'), ('E-money', 'Электронно'), ('No choice', 'Не выбрано')], db_index=True, default='No choice', max_length=16, verbose_name='Способ оплаты'),
        ),
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('Raw', 'Необработан'), ('Assembly', 'Сборка'), ('Delivery', 'Доставка'), ('Completed', 'Выполнен')], db_index=True, default='Raw', max_length=9, verbose_name='Статус заказа'),
        ),
    ]
