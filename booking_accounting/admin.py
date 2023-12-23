from django.contrib import admin

# Register your models here.
from booking_accounting.models import Booking, LoadingBooking, Transaction, CurrentBalance, Report
from vehicle_driver_app.models import Invoice

admin.site.register(Booking)
admin.site.register(LoadingBooking)
admin.site.register(Invoice)
admin.site.register(Transaction)
admin.site.register(CurrentBalance)
admin.site.register(Report)
