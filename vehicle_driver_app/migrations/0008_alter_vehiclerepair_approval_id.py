# Generated by Django 4.2.7 on 2023-12-11 18:45

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('vehicle_driver_app', '0007_approval_approval_code_driver_driver_number_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vehiclerepair',
            name='approval_id',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='approval_repair', to='vehicle_driver_app.approval'),
        ),
    ]
