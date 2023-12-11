from django.contrib import admin
from userapp.models import User, Location, Department, OTP


class AuthorAdmin(admin.ModelAdmin):
    pass
admin.site.register(User, AuthorAdmin)
admin.site.register(Location)
admin.site.register(Department)
admin.site.register(OTP)