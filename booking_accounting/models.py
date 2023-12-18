from django.db import models

# Create your models here.
from django.utils.timezone import now

from GombeLine import settings
from traffic.models import Schedule


class Booking(models.Model):
    booking_code = models.CharField(max_length=20,unique=True)
    passenger_full_name= models.CharField(max_length=50,blank=False)
    seat_no = models.IntegerField()
    passenger_phone = models.CharField(max_length=30)
    nk_full_name = models.CharField(max_length=50)
    nk_contact= models.CharField(max_length=50)
    relationship= models.CharField(max_length=50)
    schedule_id = models.ForeignKey(Schedule, related_name='booking_schedule',on_delete=models.PROTECT,blank=False)
    price = models.FloatField(default=0.0)
    payment_status = models.CharField(max_length=50)
    payment_method = models.CharField(max_length=50)
    booking_date = models.DateField(blank=True, null=True)
    modified_at = models.DateTimeField(default=now)
    created_at = models.DateTimeField(default=now)
    modified_by = models.ForeignKey(settings.AUTH_USER_MODEL,related_name='booking_modified_by', on_delete=models.SET_NULL, null=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL,related_name='booking_created_by', on_delete=models.SET_NULL, null=True)


    def __str__(self):
        return self.booking_code

class LoadingBooking(models.Model):
    loading_code = models.CharField(max_length=20)
    plate_number = models.CharField(max_length=20)
    sitting_capacity = models.IntegerField(default=0)
    cost_per_booking = models.FloatField(default=0.0)
    payment_status = models.CharField(max_length=50)
    payment_method = models.CharField(max_length=50)
    modified_at = models.DateTimeField(default=now)
    created_at = models.DateTimeField(default=now)
    modified_by = models.ForeignKey(settings.AUTH_USER_MODEL,related_name='load_modified_by', on_delete=models.SET_NULL, null=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL,related_name='load_created_by', on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.loading_code

    @property
    def charges(self):
        return self.sitting_capacity*self.cost_per_booking

class Transaction(models.Model):
    transactionId = models.CharField(max_length=20)
    description = models.CharField(max_length=50)
    orderId = models.CharField(max_length=50)
    payment_method = models.CharField(max_length=50)
    trans_method = models.CharField(max_length=50)
    amount_paid = models.FloatField(default=0.0)
    modified_at = models.DateTimeField(default=now)
    created_at = models.DateTimeField(default=now)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL,related_name='trans_created_by', on_delete=models.SET_NULL, null=True)
    modified_by = models.ForeignKey(settings.AUTH_USER_MODEL,related_name='trans_modified_by', on_delete=models.SET_NULL, null=True)



    def __str__(self):
        return self.transactionId


class Invoice(models.Model):
    invoiceId = models.CharField(max_length=20)
    purpose = models.CharField(max_length=50)
    description = models.CharField(max_length=50)
    receiver_name = models.CharField(max_length=50)
    payment_method = models.CharField(max_length=50)
    amount_paid = models.FloatField(default=0.0)
    modified_at = models.DateTimeField(default=now)
    created_at = models.DateTimeField(default=now)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL,related_name='invoice_created_by', on_delete=models.SET_NULL, null=True)
    modified_by = models.ForeignKey(settings.AUTH_USER_MODEL,related_name='invoice_modified_by', on_delete=models.SET_NULL, null=True)



    def __str__(self):
        return self.invoiceId