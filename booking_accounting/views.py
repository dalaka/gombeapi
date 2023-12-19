from django.db.models import Sum
from django.shortcuts import render

# Create your views here.
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from booking_accounting.models import Booking
from booking_accounting.serializer import BookingSerializer, BookingChangeSerializer
from booking_accounting.util import reset_bus_util
from traffic.models import Schedule
from traffic.serializer import ScheduleSerializer
from userapp.permission_decorator import response_info

custom_paginator=PageNumberPagination()
class BookingViews(viewsets.ViewSet):
    serializer_class = BookingSerializer
    permission_classes =  (IsAuthenticated,)
    queryset = Booking.objects.all().order_by('created_at')



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
        res ={'total_destination':total_des,'total_revenue':total_rev,'top_route':top_route,'top_buses':top_buses}

        return Response(response_info(status=status.HTTP_200_OK,msg="Booking statistics",data=res))

class BookingChangeViews(viewsets.ViewSet):
        serializer_class = BookingChangeSerializer
        permission_classes = (IsAuthenticated,)
        queryset = Booking.objects.all().order_by('created_at')
        oldperm = OpenApiParameter(name='old_schedule_id', description='Old Schedule Id', required=True, type=int,
                                   location=OpenApiParameter.QUERY)

        @extend_schema(parameters=[oldperm])
        def update(self, request,pk=None):
            sch_id = request.query_params.get('old_schedule_id')
            booking = get_object_or_404(self.queryset, pk=pk)
            sch = Schedule.objects.get(id=sch_id)
            if booking.expired ==True:
                return Response(response_info(status=status.HTTP_400_BAD_REQUEST, msg="Ticket Expired", data=[]))
            if Booking.objects.filter(schedule_id_id=sch_id, seat_no=request.data['seat_no']).exists():
                return Response(response_info(status=status.HTTP_400_BAD_REQUEST, msg="Seat already taken", data=[]))
            old_sch = Schedule.objects.get(id=booking.schedule_id.id)
            reset_bus_util(old_sch,request.data['seat_no'])
            serializer = BookingChangeSerializer(booking,request.data,context={'request':request,'obj': sch, 'old':old_sch})
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                return Response(response_info(status=status.HTTP_200_OK, msg='Bus changed successfully', data=serializer.data))
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
