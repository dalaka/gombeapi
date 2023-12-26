from django.urls import path, include
from rest_framework import routers

from booking_accounting import report_views

router = routers.DefaultRouter()
router.register('audilogs',  report_views.AuditViews,basename='auditlogs')
router.register('',  report_views.ReportViews,basename='report')

urlpatterns = [

    path('api/v1/', include(router.urls)),

]