from datetime import date

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
    destination = models.CharField(max_length=50)
    source = models.CharField(max_length=50, null=True)
    nk_contact= models.CharField(max_length=50)
    relationship= models.CharField(max_length=50)
    schedule_id = models.ForeignKey(Schedule, related_name='booking_schedule',on_delete=models.PROTECT,blank=False)
    amount_paid = models.FloatField(default=0.0)
    price = models.FloatField(default=0.0)
    payment_method = models.CharField(max_length=50)
    booking_date = models.DateField(blank=True, null=True)
    modified_at = models.DateTimeField(default=now)
    created_at = models.DateTimeField(default=now)
    modified_by = models.ForeignKey(settings.AUTH_USER_MODEL,related_name='booking_modified_by', on_delete=models.SET_NULL, null=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL,related_name='booking_created_by', on_delete=models.SET_NULL, null=True)


    def __str__(self):
        return self.booking_code

    def s_detail(self):
        return self.schedule_id

    @property
    def balance(self):
        if self.amount_paid>self.price:
            refund= self.amount_paid - self.price
            return {'balance': 0, 'change':refund}
        else:
            balance = self.price - self.amount_paid
            return {'balance': balance, 'change': 0}
    @property
    def expired(self):
        if  self.booking_date < date.today():
            return True
        else:
            return False
    @property
    def payment_status(self):
        if  self.amount_paid > 0 and self.price >0:
            if self.amount_paid == self.price or self.amount_paid>self.price:
                return 'Paid'
            else:
                return 'Not-Paid'
        else:
            return 'Not-Paid'
class LoadingBooking(models.Model):
    loading_code = models.CharField(max_length=20)
    plate_number = models.CharField(max_length=20)
    driver_name = models.CharField(max_length=20)
    sitting_capacity = models.IntegerField(default=0)
    cost_per_booking = models.FloatField(default=0.0)
    amount_paid = models.FloatField(default=0.0)
    loading_date = models.DateField(null=True)
    payment_method = models.CharField(max_length=50)
    modified_at = models.DateTimeField(default=now)
    created_at = models.DateTimeField(default=now)
    modified_by = models.ForeignKey(settings.AUTH_USER_MODEL,related_name='load_modified_by', on_delete=models.SET_NULL, null=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL,related_name='load_created_by', on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.loading_code

    @property
    def charges(self):
        res=0.1*(self.sitting_capacity*self.cost_per_booking)
        return round(res,2)

    @property
    def balance(self):
        return self.charges - self.amount_paid
    @property
    def expired(self):
        if  self.loading_date < date.today():
            return True
        else:
            return False

    @property
    def payment_status(self):
        if  self.amount_paid > 0 and self.charges >0:
            if self.amount_paid == self.charges:
                return 'Paid'
            else:
                return 'Not-Paid'
        else:
            return 'Not-Paid'



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