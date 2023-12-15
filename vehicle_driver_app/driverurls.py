from django.urls import path, include
from rest_framework import routers

from vehicle_driver_app import driversviews

router = routers.DefaultRouter()
router.register('',  driversviews.DriverViews,basename='driver')

urlpatterns = [
    path('api/v1/upload/', driversviews.UploadImageViews.as_view(), name='upload'),
    path('api/v1/', include(router.urls)),

    ]