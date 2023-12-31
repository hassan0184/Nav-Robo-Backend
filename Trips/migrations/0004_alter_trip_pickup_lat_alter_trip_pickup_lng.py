# Generated by Django 4.1.5 on 2023-02-04 17:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Trips', '0003_alter_trip_pickup_lat_alter_trip_pickup_lng'),
    ]

    operations = [
        migrations.AlterField(
            model_name='trip',
            name='pickup_lat',
            field=models.DecimalField(decimal_places=8, default=None, max_digits=20, verbose_name='Latitude'),
        ),
        migrations.AlterField(
            model_name='trip',
            name='pickup_lng',
            field=models.DecimalField(decimal_places=8, default=None, max_digits=20, verbose_name='Longitude'),
        ),
    ]
