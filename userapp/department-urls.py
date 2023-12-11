from django.urls import path, include
from rest_framework import routers

from userapp.views import DepartmentView
router = routers.DefaultRouter()


router.register('',  DepartmentView,'department')
urlpatterns = [

    path('api/v1/', include(router.urls)),

]