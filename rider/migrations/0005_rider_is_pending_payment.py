# Generated by Django 4.1.7 on 2023-03-02 09:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rider', '0004_rider_pending_payment'),
    ]

    operations = [
        migrations.AddField(
            model_name='rider',
            name='is_pending_payment',
            field=models.BooleanField(default=False),
        ),
    ]
