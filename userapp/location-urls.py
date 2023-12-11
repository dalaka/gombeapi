from django.urls import path, include
from rest_framework import routers

from userapp.views import LocationView
router = routers.DefaultRouter()


router.register('',  LocationView,'location')
urlpatterns = [

    path('api/v1/', include(router.urls)),

]