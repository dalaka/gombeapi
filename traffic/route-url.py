from django.urls import path, include
from rest_framework import routers

from traffic import views

router = routers.DefaultRouter()
router.register('',  views.RouteViews,basename='route')
urlpatterns = [

    path('api/v1/', include(router.urls)),

]