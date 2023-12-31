# Generated by Django 4.2.7 on 2023-12-23 09:59

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('booking_accounting', '0010_delete_invoice'),
    ]

    operations = [
        migrations.CreateModel(
            name='CurrentBalance',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('current_total_income', models.FloatField(default=0.0)),
                ('current_total_expense', models.FloatField(default=0.0)),
            ],
        ),
        migrations.CreateModel(
            name='Report',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start', models.CharField(blank=True, max_length=255)),
                ('end', models.CharField(blank=True, max_length=255)),
                ('report_type', models.CharField(blank=True, max_length=255)),
                ('total', models.CharField(blank=True, max_length=255)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('data', models.JSONField()),
            ],
        ),
    ]
