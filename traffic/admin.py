from django.contrib import admin

# Register your models here.
from traffic.models import Route, Schedule

admin.site.register(Route)
admin.site.register(Schedule)
