# Generated by Django 4.2.7 on 2023-12-01 16:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userapp', '0003_otp'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='is_verified',
            field=models.BooleanField(default=False),
        ),
    ]
