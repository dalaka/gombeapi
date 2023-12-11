from django.urls import path, include
from rest_framework import routers

from vehicle_driver_app import itemviews

router = routers.DefaultRouter()
router.register('',  itemviews.ItemViews,basename='item')
urlpatterns = [

    path('api/v1/', include(router.urls)),

]