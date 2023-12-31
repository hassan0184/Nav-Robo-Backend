# Generated by Django 4.1.5 on 2023-01-24 07:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rider', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='TransactionHistory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('customer_id', models.CharField(max_length=50)),
                ('amount', models.IntegerField()),
                ('currency', models.CharField(max_length=50)),
                ('payment_method_id', models.CharField(max_length=50)),
                ('DateTime', models.DateTimeField(blank=True, null=True)),
                ('status', models.CharField(max_length=50)),
            ],
            options={
                'verbose_name_plural': 'Transaction History',
            },
        ),
    ]
