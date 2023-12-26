from django.db.models import Sum
from django.shortcuts import render

# Create your views here.
from django.utils.timezone import now
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from booking_accounting.loading_serializer import LoadingSerializer, LoadingingPaymentSerializer
from booking_accounting.models import Booking, LoadingBooking
from booking_accounting.serializer import BookingSerializer, BookingChangeSerializer, BookingPaymentSerializer, \
    transction
from booking_accounting.util import reset_bus_util, audit_log
from traffic.models import Schedule
from traffic.serializer import ScheduleSerializer
from userapp.permission_decorator import response_info

custom_paginator=PageNumberPagination()
class BookingViews(viewsets.ViewSet):
    serializer_class = BookingSerializer
    permission_classes =  (IsAuthenticated,)
    queryset = Booking.objects.all().order_by('-created_at')



    vperam = OpenApiParameter(name='schedule_id', description='Schedule', required=True, type=int,
                              location=OpenApiParameter.QUERY)
    @extend_schema(parameters=[vperam])
    def create(self, request):

        sech=request.query_params.get('schedule_id', None)
        seat_no = request.data.get('seat_no')

        schedule = Schedule.objects.get(id=sech)
        is_vail=Booking.objects.filter(schedule_id=schedule,seat_no=seat_no,booking_date=schedule.schedule_date ).exists()
        if is_vail:
            return Response(
                response_info(status=status.HTTP_400_BAD_REQUEST, msg="Seat no already chosen", data=[]))

        serializer = BookingSerializer(data=request.data,context={'request':request,'obj':schedule})
        if serializer.is_valid(raise_exception=True):
            serializer.save()

            return Response(response_info(status=status.HTTP_201_CREATED, msg="booking created successfully", data=serializer.data))
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def list(self, request):
        res = custom_paginator.paginate_queryset(self.queryset, request)

        serializer=BookingSerializer(res, many=True)




        return custom_paginator.get_paginated_response(serializer.data)

    schperam=OpenApiParameter(name='schedule_date',description='Schedule date',required=False,type=str,location=OpenApiParameter.QUERY)
    sourceeram=OpenApiParameter(name='source',description='Pick Up State',required=False,type=str,location=OpenApiParameter.QUERY)
    desperm=OpenApiParameter(name='destination',description='Destination',required=False,type=str,location=OpenApiParameter.QUERY)

    @extend_schema(parameters=[schperam,sourceeram,desperm])
    @action(detail=False, methods=['GET'])
    def get_availabe_schedule(self, request):
        schedule_date = request.query_params.get('schedule_date')
        schedule_source = request.query_params.get('source')
        schedule_destination = request.query_params.get('destination')
        if schedule_date !=None and schedule_source !=None and schedule_destination !=None:
            s_query=Schedule.objects.filter(route_id__source=schedule_source,route_id__dest=schedule_destination,
                                            schedule_date=schedule_date).order_by('created_at')
            res = custom_paginator.paginate_queryset(s_query, request)

            serializer = ScheduleSerializer(res, many=True)

            return custom_paginator.get_paginated_response(serializer.data)

        else:
            Response(response_info(status=status.HTTP_400_BAD_REQUEST, msg='Invalid request parameter',data=[]))

    def retrieve(self, request, pk=None):
        vehicle = get_object_or_404(self.queryset, pk=pk)
        serializer = BookingSerializer(vehicle)
        return Response(response_info(status=status.HTTP_200_OK, msg="booking details", data=serializer.data))

    def destroy(self, request,pk):
        id=pk
        stu=Booking.objects.get(pk=id)
        d=stu
        stu.delete()
        desc=f"This booking {d.booking_code} has been deleted"
        audit_log(name="Booking", desc=desc, user=request.user)
        return Response(response_info(status=status.HTTP_200_OK, msg='booking delete successfully',data=[]))
    def update(self,request,pk=None):
        obj= get_object_or_404(self.queryset, pk=pk)
        serializer = BookingSerializer(obj,request.data,context={'request':request})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response({'msg': 'Data  created', 'data':serializer.data}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    bookperam=OpenApiParameter(name='booking_date',description='Booking date',required=True,type=str,location=OpenApiParameter.QUERY)
    @extend_schema(parameters=[bookperam])
    @action(detail=False, methods=['GET'])
    def get_booking_stat(self, request):
        bk_date = request.query_params.get('booking_date')
        s_query=Booking.objects.filter(booking_date=bk_date)
        total_des=Schedule.objects.filter(schedule_date=bk_date).count()
        total_rev=s_query.aggregate(Sum('price'))['price__sum']
        top_route=Booking.objects.values('schedule_id__route_id__dest').annotate(
            price=Sum('price')).filter(booking_date=bk_date)
        top_buses=Booking.objects.values('schedule_id__vehicle_id__custom_naming').annotate(
            price=Sum('price')).filter(booking_date=bk_date)
        res ={'total_destination':total_des,'total_revenue':total_rev,'total_bookings':s_query.count(),
              'top_route':top_route,'top_buses':top_buses
              }

        return Response(response_info(status=status.HTTP_200_OK,msg="Booking payment",data=res))

    @extend_schema(parameters=[bookperam])
    @action(detail=False, methods=['GET'])
    def get_recent_booking(self, request):
        bk_date = request.query_params.get('booking_date')

        bk = Booking.objects.filter(booking_date=bk_date).order_by('-created_at')
        res = custom_paginator.paginate_queryset(bk, request)

        serializer = BookingSerializer(res, many=True)

        return custom_paginator.get_paginated_response(serializer.data)

    mperam = OpenApiParameter(name='schedule_date', description='Schedule date', required=True, type=str,
                              location=OpenApiParameter.QUERY)
    mperam1 = OpenApiParameter(name='schedule_id', description='Schedule id', required=True, type=int,
                               location=OpenApiParameter.QUERY)

    @extend_schema(parameters=[mperam, mperam1])
    @action(detail=False, methods=['GET'])
    def genrate_travel_manifest(self, request):
        schedule_date = request.query_params.get('schedule_date', None)
        schedule_id = request.query_params.get('schedule_id', None)

        if schedule_date != None and schedule_id !=None:
            s_query = Booking.objects.filter(schedule_id_id=schedule_id, booking_date=schedule_date).order_by('created_at')
            expected_amount=s_query.aggregate(Sum('price'))['price__sum']
            collected_amount = s_query.aggregate(Sum('amount_paid'))['amount_paid__sum']
            serilizer=BookingSerializer(s_query,many=True)
            data={"total_passengers":s_query.count(),"expected_amount":expected_amount,
                  "collected_amount":collected_amount, "passengers":serilizer.data}

            return Response(response_info(status=status.HTTP_200_OK, msg="manifest", data=data))

class BookingPaymentViews(viewsets.ViewSet):
    serializer_class = BookingPaymentSerializer
    permission_classes = (IsAuthenticated,)
    queryset = Booking.objects.all().order_by('created_at')


    def update(self, request, pk=None):

        bk_obj=get_object_or_404(self.queryset, pk=pk)

        if bk_obj.payment_status =='Paid':
            return Response(response_info(status=status.HTTP_401_UNAUTHORIZED, msg="This booking is paid", data=[]))
        else:
            bk_obj.amount_paid += request.data.get('amount')
            bk_obj.payment_method = request.data.get('payment_method')
            bk_obj.modified_by = request.user
            bk_obj.modified_at = now()
            bk_obj.save()
            transction(user=request.user, orderid=bk_obj.booking_code, price=request.data.get('amount'), des='Booking',
                       paymet_method=request.data.get('payment_method'), trnx_method='Credit')
            return Response(response_info(status=status.HTTP_200_OK,msg="Payment made successfully", data=[]))



class BookingChangeViews(viewsets.ViewSet):
        serializer_class = BookingChangeSerializer
        permission_classes = (IsAuthenticated,)
        queryset = Booking.objects.all().order_by('created_at')
        oldperm = OpenApiParameter(name='schedule_id', description='Schedule Id', required=True, type=int,
                                   location=OpenApiParameter.QUERY)

        @extend_schema(parameters=[oldperm])
        def update(self, request,pk=None):
            sch_id = request.query_params.get('schedule_id')
            booking = get_object_or_404(self.queryset, pk=pk)
            sch = Schedule.objects.get(id=sch_id)
            if booking.expired ==True:
                return Response(response_info(status=status.HTTP_400_BAD_REQUEST, msg="Ticket Expired", data=[]))
            if Booking.objects.filter(schedule_id_id=sch_id, seat_no=request.data['seat_no']).exists():
                return Response(response_info(status=status.HTTP_400_BAD_REQUEST, msg="Seat already taken", data=[]))
            old_sch = Schedule.objects.get(id=booking.schedule_id.id)
            reset_bus_util(old_sch,booking.seat_no)
            serializer = BookingChangeSerializer(booking,request.data,context={'request':request,'obj': sch, 'old':old_sch})
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                return Response(response_info(status=status.HTTP_200_OK, msg='Bus changed successfully', data=serializer.data))
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class LoadingViews(viewsets.ViewSet):
    serializer_class = LoadingSerializer
    permission_classes =  (IsAuthenticated,)
    queryset = LoadingBooking.objects.all().order_by('-created_at')

    def create(self, request):
        serializer = LoadingSerializer(data=request.data,context={'request':request})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(response_info(status=status.HTTP_201_CREATED, msg="loading created successfully", data=serializer.data))
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def list(self, request):

        res = custom_paginator.paginate_queryset(self.queryset, request)

        serializer=LoadingSerializer(res, many=True)




        return custom_paginator.get_paginated_response(serializer.data)




    def retrieve(self, request, pk=None):
        vehicle = get_object_or_404(self.queryset, pk=pk)
        serializer = LoadingSerializer(vehicle)
        return Response(response_info(status=status.HTTP_200_OK, msg="schedule details", data=serializer.data))

    def update(self,request,pk=None):
        item = get_object_or_404(self.queryset, pk=pk)
        serializer = LoadingSerializer(item,request.data,context={'request':request})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response({'msg': 'Data  created', 'data':serializer.data}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    def destroy(self, request,pk):
        id=pk
        stu=LoadingBooking.objects.get(pk=id)
        d=stu.loading_code
        stu.delete()

        desc=f"This loading {d} has been deleted"
        audit_log(name="Loading", desc=desc, user=request.user)
        return Response(response_info(status=status.HTTP_200_OK, msg='loading delete successfully',data=[]))


class LoadingPaymentViews(viewsets.ViewSet):
    serializer_class = LoadingingPaymentSerializer
    permission_classes = (IsAuthenticated,)
    queryset = LoadingBooking.objects.all().order_by('created_at')


    def update(self, request, pk=None):

        bk_obj=get_object_or_404(self.queryset, pk=pk)

        if bk_obj.payment_status =='Paid':
            return Response(response_info(status=status.HTTP_401_UNAUTHORIZED, msg="This loading is paid", data=[]))
        else:
            bk_obj.amount_paid += request.data.get('amount')
            bk_obj.payment_method = request.data.get('payment_method')
            bk_obj.modified_by = request.user
            bk_obj.modified_at = now()
            bk_obj.save()
            transction(user=request.user, orderid=bk_obj.loading_code, price=request.data.get('amount'), des='Booking',
                       paymet_method=request.data.get('payment_method'), trnx_method='Credit')
            return Response(response_info(status=status.HTTP_200_OK,msg="Payment made successfully", data=[]))


