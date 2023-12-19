from django.urls import path, include
from rest_framework import routers

from booking_accounting import views

router = routers.DefaultRouter()
router.register('',  views.BookingViews,basename='booking')
router.register('change-bus',  views.BookingChangeViews,basename='change-booking')
urlpatterns = [

    path('api/v1/', include(router.urls)),

]