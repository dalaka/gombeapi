# Generated by Django 4.2.7 on 2023-12-06 18:55

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vehicle_driver_app', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='driver',
            old_name='nk_conytact',
            new_name='nk_contact',
        ),
        migrations.RemoveField(
            model_name='driver',
            name='number_of_trips',
        ),
    ]
