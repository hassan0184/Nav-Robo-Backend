# Generated by Django 4.1.5 on 2023-02-01 06:50

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('robot', '0002_rename_basicdeatils_basicinfo'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='basicinfo',
            options={'verbose_name_plural': 'Robot Information'},
        ),
    ]