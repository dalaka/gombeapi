from django.urls import path, include
from rest_framework import routers

from traffic import views

router = routers.DefaultRouter()
router.register('',  views.ScheduleViews,basename='schedule')
urlpatterns = [

    path('api/v1/', include(router.urls)),

]