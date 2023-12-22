from django.urls import path, include
from rest_framework import routers

from booking_accounting import trnx_views

router = routers.DefaultRouter()
router.register('transactions',  trnx_views.TransactionViews,basename='transactions')
router.register('',  trnx_views.InvoiceViews,basename='invoice')
router.register('invoice-payment',  trnx_views.InvoicePaymentViews,basename='invoice-payment')

urlpatterns = [

    path('api/v1/', include(router.urls)),

]