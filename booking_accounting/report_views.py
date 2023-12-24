import datetime
from datetime import date
import pandas as pd
from django.db.models import Sum
from django.utils.timezone import now
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from booking_accounting.models import Transaction, Booking, Report
from booking_accounting.serializer import transction
from booking_accounting.trnx_serializer import InvoiceSerializer, InvoicePaymentSerializer, TransactionSerializer, \
    ReportSerializer, BookingReportSerializer, VehicleRepairReportSerializer
from booking_accounting.util import last_thirtydays, create_report
from userapp.permission_decorator import response_info
from vehicle_driver_app.models import Invoice, VehicleRepair

custom_paginator=PageNumberPagination()

class ReportViews(viewsets.ViewSet):
    serializer_class = ReportSerializer
    permission_classes =  (IsAuthenticated,)
    queryset = Report.objects.all().order_by('-created_at')

    def create(self, request):
        report_type = request.data.get('report_type')

        start_d=date.today().strftime('%Y-%m-01')
        end_d = date.today().strftime('%Y-%m-%d')

        s_date=request.data.get('start', start_d)
        e_date= request.data.get('end',end_d)

        s = f"{s_date} 00:00:00"
        e = f"{e_date} 23:59:59"
        if report_type == 'booking':
            bk_obj = Booking.objects.filter(created_at__range=[s,e])

            total = bk_obj.aggregate(Sum('amount_paid'))['amount_paid__sum']
            if total == None:
                total =0.0

            data=BookingReportSerializer(bk_obj, many=True)
            report_obj=create_report(s=s,e=e,report_type=report_type, total=total,data=data.data)
            res = self.serializer_class(report_obj)
            return Response(response_info(status=status.HTTP_200_OK, msg="report generated successfully",
                                          data=res.data))
        if report_type == 'repair':
            print(e)
            print(s)
            bk_obj = VehicleRepair.objects.filter(created_at__range=[s,e])
            print(bk_obj)
            total = bk_obj.aggregate(Sum('repair_cost'))['repair_cost__sum']
            if total == None:
                total =0.0

            data=VehicleRepairReportSerializer(bk_obj, many=True)
            report_obj=create_report(s=s,e=e,report_type=report_type, total=total,data=data.data)
            res = self.serializer_class(report_obj)
            return Response(response_info(status=status.HTTP_200_OK, msg="report generated successfully",
                                          data=res.data))

        return Response(response_info(status=status.HTTP_401_UNAUTHORIZED, msg="Report can not be created", data=[]))

    def list(self, request):

        res = custom_paginator.paginate_queryset(self.queryset, request)

        serializer=self.serializer_class(res, many=True)



        return custom_paginator.get_paginated_response(serializer.data)




    def retrieve(self, request, pk=None):
        vehicle = get_object_or_404(self.queryset, pk=pk)
        serializer =self.serializer_class(vehicle)
        return Response(response_info(status=status.HTTP_200_OK, msg="report details", data=serializer.data))


    def destroy(self, request,pk):
        id=pk
        stu=Report.objects.get(pk=id)
        stu.delete()
        return Response(response_info(status=status.HTTP_200_OK, msg='report deleted successfully',data=[]))

