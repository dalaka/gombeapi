# Generated by Django 4.2.7 on 2023-12-26 14:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('booking_accounting', '0013_auditlog'),
    ]

    operations = [
        migrations.AddField(
            model_name='auditlog',
            name='audit_type',
            field=models.CharField(default=1, max_length=100),
            preserve_default=False,
        ),
    ]
