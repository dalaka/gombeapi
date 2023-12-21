import os
from datetime import date

from django.db import models

# Create your models here.
from django.utils.timezone import now

from GombeLine import settings

from userapp.models import BaseModel
from userapp.utils import generate_activation_code
def upload_to(instance, filename):
    return os.path.join('image',str(instance.id), filename)

class Invoice(models.Model):
    invoiceId = models.CharField(max_length=20)
    purpose = models.CharField(max_length=50)
    description = models.CharField(max_length=50,null=True)
    receiver_name = models.CharField(max_length=50, null=True)
    payment_method = models.CharField(max_length=50, null=True)
    invoice_total = models.FloatField(default=0.0)
    amount_paid = models.FloatField(default=0.0)
    modified_at = models.DateTimeField(default=now)
    created_at = models.DateTimeField(default=now)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL,related_name='invoice_created_by', on_delete=models.SET_NULL, null=True)
    modified_by = models.ForeignKey(settings.AUTH_USER_MODEL,related_name='invoice_modified_by', on_delete=models.SET_NULL, null=True)
    is_approved= models.BooleanField(default=False)
    approved_by = models.CharField(max_length=250,blank=False)


    def __str__(self):
        return self.invoiceId
class Item(models.Model):

    modified_at = models.DateTimeField(default=now)
    created_at = models.DateTimeField(default=now)
    modified_by = models.ForeignKey(settings.AUTH_USER_MODEL,related_name='item_modified_by', on_delete=models.SET_NULL, null=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL,related_name='item_created_by', on_delete=models.SET_NULL, null=True)
    name =models.CharField(max_length=100)
    quantity = models.IntegerField()
    def __str__(self):
        return self.name
    @property
    def isavailable(self):
        if self.quantity ==0:
            return False
        else:
            return True

class Driver(models.Model):

    modified_at = models.DateTimeField(default=now)
    created_at = models.DateTimeField(default=now)
    image = models.ImageField(upload_to=upload_to, blank=True, null=True)
    modified_by = models.ForeignKey(settings.AUTH_USER_MODEL,related_name='dr_modified_by', on_delete=models.SET_NULL, null=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL,related_name='dr_created_by', on_delete=models.SET_NULL, null=True)
    driver_number = models.CharField(max_length=50, null=True)
    first_name =models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone =models.CharField(max_length=100, unique=True)
    address = models.CharField(max_length=100)
    driver_license =models.CharField(max_length=100)
    expiry_date = models.DateField(blank=False)
    nk_full_name =models.CharField(max_length=100)
    nk_contact = models.CharField(max_length=100,blank=False)
    relationship  = models.CharField(max_length=50,blank=False)
    nk_address = models.CharField(max_length=100,blank=False)

    def __str__(self):
        return self.first_name

    @property
    def number_trips(self):

        logs = DriverLog.objects.filter(driver_id=self.id)
        return len(logs)

    @property
    def is_license_active(self):
        if date.today() < self.expiry_date:
            return True
        else:
            return False

class DriverLog(models.Model):

    driver_id = models.ForeignKey(Driver, related_name='deriver_log',on_delete=models.PROTECT)
    departure = models.CharField(max_length=100,blank=False)
    destination = models.CharField(max_length=100,blank=False)
    vehicle_name = models.CharField(max_length=100, blank=True, null=True)
    datetime_daparture = models.DateField()
    is_arrived = models.BooleanField(default=False)
    datetime_destination= models.DateTimeField(default=now)

class Vehicle(models.Model):

    modified_at = models.DateTimeField(default=now)
    created_at = models.DateTimeField(default=now)
    modified_by = models.ForeignKey(settings.AUTH_USER_MODEL,related_name='vehicle_modified_by', on_delete=models.SET_NULL, null=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL,related_name='vehicle_created_by', on_delete=models.SET_NULL, null=True)
    vehicle_make=models.CharField(max_length=100,blank=False)
    vehicle_model =models.CharField(max_length=100,blank=False)
    vin = models.CharField(max_length=100, unique=True)
    reg_number  =models.CharField(max_length=100, unique=True)
    vehicle_type = models.CharField(max_length=100,blank=False)
    color = models.CharField(max_length=100,blank=False)
    sitting_capacity= models.CharField(max_length=100,blank=False)
    custom_naming= models.CharField(max_length=100,blank=False)
    vehicle_condition= models.CharField(max_length=100,blank=False)
    is_available= models.BooleanField(default=True)

    def __str__(self):
        return self.custom_naming

    def maintaince_history(self):
        return  Maintenance.objects.filter(vehicle_id=self)



    def repair_history(self):
        return VehicleRepair.objects.filter(vehicle_id=self)

class Approval(models.Model):
    approval_code = models.CharField(max_length=50, null=True)
    modified_at = models.DateTimeField(default=now)
    created_at = models.DateTimeField(default=now)
    modified_by = models.ForeignKey(settings.AUTH_USER_MODEL,related_name='approval_modified_by', on_delete=models.SET_NULL, null=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL,related_name='approval_created_by', on_delete=models.SET_NULL, null=True)
    approval_type = models.CharField(max_length=250,blank=False)
    is_approved= models.BooleanField(default=False)
    approved_by = models.CharField(max_length=250,blank=False)
    def __str__(self):
        return self.approval_code

class Maintenance(models.Model):
    maintenance_code = models.CharField(max_length=50, null=True)
    modified_at = models.DateTimeField(default=now)
    created_at = models.DateTimeField(default=now)
    modified_by = models.ForeignKey(settings.AUTH_USER_MODEL,related_name='main_modified_by', on_delete=models.SET_NULL, null=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL,related_name='main_created_by', on_delete=models.SET_NULL, null=True)
    vehicle_id = models.ForeignKey(Vehicle, related_name='vehicle_maintenance',on_delete=models.PROTECT)
    maintenance_date = models.DateField()
    due_date = models.DateField()
    maintenance_type = models.ManyToManyField(Item)
    maintenance_cost = models.FloatField()
    invoice_id = models.ForeignKey(Invoice, related_name='invoice_maintenance',on_delete=models.PROTECT, null=True)
    approval_id = models.ForeignKey(Approval, related_name='approval_maintenance', on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.maintenance_code

    def vehicle_d(self):
        return self.vehicle_id



class VehicleRepair(models.Model):
    repair_code = models.CharField(max_length=50, null=True)
    modified_at = models.DateTimeField(default=now)
    created_at = models.DateTimeField(default=now)
    modified_by = models.ForeignKey(settings.AUTH_USER_MODEL,related_name='repair_modified_by', on_delete=models.SET_NULL, null=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL,related_name='repair_created_by', on_delete=models.SET_NULL, null=True)
    vehicle_id = models.ForeignKey(Vehicle, related_name='repairs_maintenance',on_delete=models.PROTECT)
    repair_date = models.DateField()
    repair_descriptions = models.CharField(max_length=250,blank=False)
    repair_cost = models.FloatField()
    approval_id = models.ForeignKey(Approval, related_name='approval_repair',on_delete=models.PROTECT,null=True)
    invoice_id = models.ForeignKey(Invoice, related_name='invoice_repair',on_delete=models.PROTECT, null=True)

    def __str__(self):
        return self.repair_code

    def vehicle_d(self):
        return self.vehicle_id



