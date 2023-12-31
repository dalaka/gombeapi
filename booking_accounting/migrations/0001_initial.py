# Generated by Django 4.2.7 on 2023-12-18 06:58

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('traffic', '0002_schedule_seats_available_alter_schedule_name'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('transactionId', models.CharField(max_length=20)),
                ('description', models.CharField(max_length=50)),
                ('orderId', models.CharField(max_length=50)),
                ('trans_method', models.CharField(max_length=50)),
                ('amount_paid', models.FloatField(default=0.0)),
                ('modified_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='trans_created_by', to=settings.AUTH_USER_MODEL)),
                ('modified_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='trans_modified_by', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='LoadingBooking',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('loading_code', models.CharField(max_length=20)),
                ('plate_number', models.CharField(max_length=20)),
                ('sitting_capacity', models.IntegerField(default=0)),
                ('cost_per_booking', models.FloatField(default=0.0)),
                ('payment_status', models.CharField(max_length=50)),
                ('payment_method', models.CharField(max_length=50)),
                ('modified_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='load_created_by', to=settings.AUTH_USER_MODEL)),
                ('modified_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='load_modified_by', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Invoice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('invoiceId', models.CharField(max_length=20)),
                ('purpose', models.CharField(max_length=50)),
                ('description', models.CharField(max_length=50)),
                ('receiver_name', models.CharField(max_length=50)),
                ('payment_method', models.CharField(max_length=50)),
                ('amount_paid', models.FloatField(default=0.0)),
                ('modified_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='invoice_created_by', to=settings.AUTH_USER_MODEL)),
                ('modified_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='invoice_modified_by', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Booking',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('booking_code', models.CharField(max_length=20, unique=True)),
                ('passenger_full_name', models.CharField(max_length=50)),
                ('seat_no', models.CharField(max_length=4)),
                ('passenger_phone', models.CharField(max_length=30)),
                ('nk_full_name', models.CharField(max_length=50)),
                ('nk_contact', models.CharField(max_length=50)),
                ('relationship', models.CharField(max_length=50)),
                ('price', models.FloatField(default=0.0)),
                ('payment_status', models.CharField(max_length=50)),
                ('payment_method', models.CharField(max_length=50)),
                ('modified_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='booking_created_by', to=settings.AUTH_USER_MODEL)),
                ('modified_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='booking_modified_by', to=settings.AUTH_USER_MODEL)),
                ('schedule_id', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='booking_schedule', to='traffic.schedule')),
            ],
        ),
    ]
