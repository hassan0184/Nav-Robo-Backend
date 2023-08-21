# Generated by Django 4.1.5 on 2023-02-03 07:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('operators', '0003_alter_operator_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='operator',
            name='status',
            field=models.CharField(blank=True, choices=[('Online', 'Online'), ('Offline', 'Offline')], default='Offline', max_length=50, null=True),
        ),
    ]
