# Generated by Django 4.2.7 on 2023-12-18 10:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('booking_accounting', '0003_booking_booking_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='booking',
            name='seat_no',
            field=models.IntegerField(),
        ),
    ]
