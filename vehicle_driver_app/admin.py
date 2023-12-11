from django.contrib import admin

from vehicle_driver_app.models import Driver, DriverLog,Maintenance,VehicleRepair,Vehicle, Item, Approval

admin.site.register(Driver)
admin.site.register(DriverLog)
admin.site.register(Vehicle)
admin.site.register(Maintenance)
admin.site.register(VehicleRepair)
admin.site.register(Item)
admin.site.register(Approval)