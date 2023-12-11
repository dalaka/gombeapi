from django.urls import path, include
from rest_framework import routers

from vehicle_driver_app import vehicleviews

router = routers.DefaultRouter()
router.register('',  vehicleviews.MaintenanceViews,basename='maintenance')
urlpatterns = [

    path('api/v1/', include(router.urls)),

]