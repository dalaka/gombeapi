from django.contrib import admin

# Register your models here.
from booking_accounting.models import Booking, LoadingBooking, Invoice, Transaction

admin.site.register(Booking)
admin.site.register(LoadingBooking)
admin.site.register(Invoice)
admin.site.register(Transaction)

