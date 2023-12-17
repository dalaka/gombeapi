from django.db import models

# Create your models here.
from django.utils.timezone import now

from GombeLine import settings
from vehicle_driver_app.models import Driver, Vehicle


class Route(models.Model):
    name= models.CharField(max_length=50,unique=True)
    source = models.CharField(max_length=30)
    dest = models.CharField(max_length=30)
    modified_at = models.DateTimeField(default=now)
    created_at = models.DateTimeField(default=now)
    modified_by = models.ForeignKey(settings.AUTH_USER_MODEL,related_name='route_modified_by', on_delete=models.SET_NULL, null=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL,related_name='route_created_by', on_delete=models.SET_NULL, null=True)


    def __str__(self):
        return  self.name

    def to_g(self):
        return Schedule.objects.filter(route_id=self)


class Schedule(models.Model):

    route_id = models.ForeignKey(Route, related_name='schedule_route', on_delete=models.PROTECT)
    name= models.CharField(max_length=50)
    driver_id = models.ForeignKey(Driver, related_name='driver_sch', on_delete=models.SET_NULL, null=True)
    vehicle_id = models.ForeignKey(Vehicle, related_name='vehicle_sch', on_delete=models.SET_NULL,null=True)
    price=models.FloatField()
    modified_at = models.DateTimeField(default=now)
    seats= models.JSONField()
    seats_available = models.IntegerField()
    schedule_date = models.DateField()
    created_at = models.DateTimeField(default=now)
    modified_by = models.ForeignKey(settings.AUTH_USER_MODEL,related_name='sch_modified_by', on_delete=models.SET_NULL, null=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL,related_name='sch_created_by', on_delete=models.SET_NULL, null=True)


    def __str__(self):
        return  self.name


    def driver_detail(self):
         return self.driver_id

    def vehicle_detail(self):
         return self.vehicle_id

    def route_d(self):
         return self.route_id