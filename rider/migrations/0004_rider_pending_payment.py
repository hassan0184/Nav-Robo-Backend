# Generated by Django 4.1.7 on 2023-03-01 07:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rider', '0003_transactionhistory_rider'),
    ]

    operations = [
        migrations.AddField(
            model_name='rider',
            name='pending_payment',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
