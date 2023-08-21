# Generated by Django 4.1.5 on 2023-02-16 11:43

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('robot', '0004_alter_basicinfo_robot_id'),
        ('rider', '0003_transactionhistory_rider'),
        ('Trips', '0006_alter_trip_estimating_time'),
    ]

    operations = [
        migrations.AlterField(
            model_name='trip',
            name='rider',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='rider.rider'),
        ),
        migrations.AlterField(
            model_name='trip',
            name='robot',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='robot.basicinfo'),
        ),
        migrations.AlterField(
            model_name='trip',
            name='status',
            field=models.CharField(choices=[('initiated', 'initiated'), ('Started', 'Started'), ('Completed', 'Completed'), ('Canceled', 'Canceled')], default='initiated', max_length=255),
        ),
    ]
