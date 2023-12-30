import datetime
from datetime import date
import pandas as pd
from django.db.models import Sum, Q
from django.utils.timezone import now
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from booking_accounting.models import Transaction, Booking, CurrentBalance
from booking_accounting.serializer import transction
from booking_accounting.trnx_serializer import InvoiceSerializer, InvoicePaymentSerializer, TransactionSerializer, \
    InvoiceFilter
from booking_accounting.util import last_thirtydays
from userapp.permission_decorator import response_info
from vehicle_driver_app.models import Invoice, VehicleRepair

custom_paginator=PageNumberPagination()

class InvoiceViews(viewsets.ViewSet):
    serializer_class = InvoiceSerializer
    permission_classes =  (IsAuthenticated,)
    queryset = Invoice.objects.all().order_by('-created_at')

    def create(self, request):
        serializer = self.serializer_class(data=request.data,context={'request':request})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(response_info(status=status.HTTP_201_CREATED, msg="invoice created successfully", data=serializer.data))
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    @action(detail=False, methods=['GET'])
    def chairman_invoice_list(self, request):
        search = request.query_params.get('search', None)

        queryset = Invoice.objects.filter(invoice_total__gt=100000).order_by('-created_at')
        if search !=None:
            queryset = queryset.filter(Q(invoiceId=search))
        filterset = InvoiceFilter(request.GET, queryset=queryset)
        if filterset.is_valid():
            queryset = filterset.qs
        res = custom_paginator.paginate_queryset(queryset, request)

        serializer=InvoiceSerializer(res, many=True)



        return custom_paginator.get_paginated_response(serializer.data)

    def list(self, request):
        search = request.query_params.get('search', None)

        queryset = Invoice.objects.filter(invoice_total__lte=100000).order_by('-created_at')
        if search !=None:
            queryset = queryset.filter(Q(invoiceId=search))
        filterset = InvoiceFilter(request.GET, queryset=queryset)
        if filterset.is_valid():
            queryset = filterset.qs
        res = custom_paginator.paginate_queryset(queryset, request)

        serializer=InvoiceSerializer(res, many=True)



        return custom_paginator.get_paginated_response(serializer.data)

    def retrieve(self, request, pk=None):
        vehicle = get_object_or_404(self.queryset, pk=pk)
        serializer =InvoiceSerializer(vehicle)
        return Response(response_info(status=status.HTTP_200_OK, msg="schedule details", data=serializer.data))

    def update(self,request,pk=None):
        item = get_object_or_404(self.queryset, pk=pk)
        serializer = self.serializer_class(item,request.data,context={'request':request})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response({'msg': 'Data  created', 'data':serializer.data}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    def destroy(self, request,pk):
        id=pk
        stu=Invoice.objects.get(pk=id)
        stu.delete()
        return Response(response_info(status=status.HTTP_200_OK, msg='loading delete successfully',data=[]))


class InvoicePaymentViews(viewsets.ViewSet):
    serializer_class = InvoicePaymentSerializer
    permission_classes = (IsAuthenticated,)
    queryset = Invoice.objects.all().order_by('created_at')
    def update(self, request, pk=None):
        balance=CurrentBalance.objects.get(id=1)
        bk_obj=get_object_or_404(self.queryset, pk=pk)
        amt =request.data.get('amount')
        if amt > balance.current_total_income:
            return Response(response_info(status=status.HTTP_401_UNAUTHORIZED, msg="No enough credit to settle this invoice", data=[]))
        if bk_obj.invoice_status =='Paid':
            return Response(response_info(status=status.HTTP_401_UNAUTHORIZED, msg="This invoice is paid", data=[]))


        else:
            bk_obj.amount_paid += request.data.get('amount')
            bk_obj.payment_method = request.data.get('payment_method')
            bk_obj.receiver_name = request.data.get('receiver_name')
            bk_obj.is_approved = request.data.get('is_approved')
            bk_obj.modified_by = request.user
            bk_obj.approved_by = f"{request.user.first_name} {request.user.last_name}"
            bk_obj.modified_at = now()
            bk_obj.save()
            transction(user=request.user, orderid=bk_obj.invoiceId, price=request.data.get('amount'), des=bk_obj.description,
                       paymet_method=request.data.get('payment_method'), trnx_method='Expense')
            return Response(response_info(status=status.HTTP_200_OK,msg="Payment made successfully", data=[]))


class TransactionViews(viewsets.ViewSet):
    serializer_class = TransactionSerializer
    permission_classes =  (IsAuthenticated,)
    queryset = Transaction.objects.all().order_by('-created_at')

    sdperm = OpenApiParameter(name='start_date', description='start date', required=False, type=str,
                               location=OpenApiParameter.QUERY)
    edperm = OpenApiParameter(name='end_date', description='end date', required=False, type=str,
                               location=OpenApiParameter.QUERY)
    @extend_schema(parameters=[sdperm,edperm])
    def list(self, request):
        start_d=date.today().strftime('%Y-%m-01')
        end_d = date.today().strftime('%Y-%m-%d')

        s_date=request.query_params.get('start_date', start_d)
        e_date= request.query_params.get('end_date',end_d)

        s = f"{s_date} 00:00:00"
        e = f"{e_date} 23:59:59"
        trn=Transaction.objects.filter(created_at__range=[s,e]).order_by('-created_at')
        res = custom_paginator.paginate_queryset(trn, request)

        serializer=self.serializer_class(res, many=True)



        return custom_paginator.get_paginated_response(serializer.data)

    @extend_schema(parameters=[sdperm, edperm])
    @action(detail=False, methods=['GET'])
    def account_dashboard_stat(self, request, *args, **kwargs):
        data=[]
        start_d=date.today().strftime('%Y-01-01')
        end_d = date.today().strftime('%Y-%m-%d')

        s_date=request.query_params.get('start_date', start_d)
        e_date= request.query_params.get('end_date',end_d)
        year=datetime.datetime.strptime(s_date, "%Y-%m-%d").date()

        month_list = pd.period_range(start=s_date, end=e_date, freq='M')
        month_list = [month.strftime("%m") for month in month_list]
        total_income = Transaction.objects.filter(created_at__year=year.year,trans_method='Credit').aggregate(
            Sum('amount_paid'))['amount_paid__sum']
        total_expense = Transaction.objects.filter(created_at__year=year.year,trans_method='Expense').aggregate(
            Sum('amount_paid'))['amount_paid__sum']

        for i in month_list:
            total=Transaction.objects.filter(created_at__month=i,created_at__year=year.year).aggregate(Sum(
                'amount_paid'))['amount_paid__sum']
            if total==None:
                total=0.0
            ress = {"month": i, "total": total}
            data.append(ress)
        if total_income==None:
            total_income =0
        if total_expense==None:
            total_expense =0
        balance=total_income-total_expense

        k=last_thirtydays(30)
        bk_total= Booking.objects.filter(created_at__range=[k['start_dt'], k['end_dt']]
                                         ).aggregate(Sum('amount_paid'))['amount_paid__sum']

        repair_total= VehicleRepair.objects.filter(created_at__range=[k['start_dt'], k['end_dt']]
                                         ).aggregate(Sum('repair_cost'))['repair_cost__sum']
        expense_total= Transaction.objects.filter(created_at__range=[k['start_dt'], k['end_dt']], trans_method="Expense"
                                         ).aggregate(Sum('amount_paid'))['amount_paid__sum']
        over_view={"booking_total":bk_total, "repair_cost":repair_total, "expense_total": expense_total}
        res = {"total_income": total_income,"balance":balance, "total_expense": total_expense,
               "over_view":over_view, "data":data}
        return Response({"message": "dashboard", "result": res}, status=status.HTTP_200_OK)

    def retrieve(self, request, pk=None):
        vehicle = get_object_or_404(self.queryset, pk=pk)
        serializer =self.serializer_class(vehicle)
        return Response(response_info(status=status.HTTP_200_OK, msg="transaction details", data=serializer.data))

