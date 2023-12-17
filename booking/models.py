from django.db import models

# Create your models here.
from django.utils.timezone import now

from GombeLine import settings


class Booking(models.Model):
    passenger_name= models.CharField(max_length=50)
    modified_at = models.DateTimeField(default=now)
    created_at = models.DateTimeField(default=now)
    modified_by = models.ForeignKey(settings.AUTH_USER_MODEL,related_name='route_modified_by', on_delete=models.SET_NULL, null=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL,related_name='route_created_by', on_delete=models.SET_NULL, null=True)
