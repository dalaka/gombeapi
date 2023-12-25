import datetime
from datetime import date
import pandas as pd
from django.db.models import Sum, Count
from django.utils.timezone import now
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from booking_accounting.models import Transaction, Booking, Report, CurrentBalance
from booking_accounting.serializer import transction
from booking_accounting.trnx_serializer import InvoiceSerializer, InvoicePaymentSerializer, TransactionSerializer, \
    ReportSerializer, BookingReportSerializer, VehicleRepairReportSerializer, BalanceSerializer
from booking_accounting.util import last_thirtydays, create_report
from traffic.models import Schedule
from userapp.permission_decorator import response_info
from vehicle_driver_app.models import Invoice, VehicleRepair, Vehicle, Driver

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

    sdperm = OpenApiParameter(name='search_date', description='search date', required=False, type=str,
                              location=OpenApiParameter.QUERY)
    @extend_schema(parameters=[sdperm])
    @action(detail=False, methods=['GET'])
    def executive_dashboard_stat(self, request, *args, **kwargs):
        data=[]
        start_d=date.today().strftime('%Y-%m-01')

        s_date=request.query_params.get('search_date', start_d)
        search_date=datetime.datetime.strptime(s_date, "%Y-%m-%d").date()

        current=CurrentBalance.objects.get(id=1)
        current_blances = BalanceSerializer(current)

        total_vehicles= Vehicle.objects.all().count()
        total_drivers = Driver.objects.all().count()
        current_position={"current_balances": current_blances.data, "total_vehicle":total_vehicles,
                          "total_drivers":total_drivers}

        total_income_year = Transaction.objects.filter(created_at__year=search_date.year,trans_method='Credit').aggregate(
            Sum('amount_paid'))['amount_paid__sum']
        total_income_month = Transaction.objects.filter(created_at__year=search_date.year,created_at__month=search_date.month,
                                                        trans_method='Credit').aggregate(Sum('amount_paid'))['amount_paid__sum']
        total_expense_year = Transaction.objects.filter(created_at__year=search_date.year,trans_method='Expense').aggregate(
            Sum('amount_paid'))['amount_paid__sum']
        total_expense_month = Transaction.objects.filter(created_at__year=search_date.year,created_at__month=search_date.month,
                                                         trans_method='Expense').aggregate(Sum('amount_paid'))['amount_paid__sum']

        if total_income_year==None:
            total_income_year =0
        if total_income_month==None:
            total_income_month =0
        if total_expense_year==None:
            total_expense_year =0
        if total_expense_month==None:
            total_expense_month =0

        for i in ['01', '02','03', '04','05','06','07','08','09', '10','11','12']:
            total=Transaction.objects.filter(trans_method='Credit',created_at__month=i,
                                             created_at__year=search_date.year).aggregate(Sum(
                'amount_paid'))['amount_paid__sum']
            total_ex = Transaction.objects.filter(trans_method='Expense',created_at__month=i,
                                                  created_at__year=search_date.year).aggregate(Sum(
                'amount_paid'))['amount_paid__sum']
            if total==None:
                total=0.0
            if total_ex==None:
                total_ex=0.0
            ress = {"month": i, "income_total": total, "expense_total":total_ex}
            data.append(ress)


        top_route_year=Schedule.objects.values('route_id__dest').annotate(
            total=Count('route_id__dest')).filter(schedule_date__year=search_date.year)

        top_route_month=Schedule.objects.values('route_id__dest').annotate(
            total=Count('route_id__dest')).filter(schedule_date__month=search_date.month)
        balance_year=total_income_year-total_expense_year
        balance_month = total_income_month - total_expense_month
        year_position={"total_income_year":total_income_year,"total_expense_year":total_expense_year, "profit":
                       balance_year}
        month_position={"total_income_month":total_income_month,"total_expense_month":total_expense_month, "profit":
                       balance_month}
        res = {"current_position": current_position,"year_position":year_position,
               "month_position": month_position, "top_routes_year": top_route_year, "top_routes_month":top_route_month,
               'data':data}
        return Response({"message": "dashboard", "result": res}, status=status.HTTP_200_OK)
