from django.db.models import Q
from django.shortcuts import render

# Create your views here.
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from booking_accounting.util import audit_log
from traffic.models import Route, Schedule
from traffic.serializer import RouteSerializer, ScheduleSerializer
from traffic.utils import grouped_schedule
from userapp.permission_decorator import response_info

custom_paginator=PageNumberPagination()

class RouteViews(viewsets.ViewSet):
    serializer_class = RouteSerializer
    permission_classes =  (IsAuthenticated,)
    queryset = Route.objects.all().order_by('created_at')

    def create(self, request):
        serializer = RouteSerializer(data=request.data,context={'request':request})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(response_info(status=status.HTTP_201_CREATED, msg="route created successfully", data=serializer.data))
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    vperam = OpenApiParameter(name='search', description='search vehicle', required=False, type=str,
                              location=OpenApiParameter.QUERY)
    @extend_schema(parameters=[vperam])
    def list(self, request, *args, **kwargs):
        search = request.query_params.get('search', None)
        if search != None:
            all_route = Route.objects.filter(Q(name__contains=search)|Q(source__icontains=search)|Q(dest__icontains=search))
        else:
            all_route = self.queryset
        res = custom_paginator.paginate_queryset(all_route, request)
        serializer=RouteSerializer(res, many=True)
        return custom_paginator.get_paginated_response(serializer.data)

    def retrieve(self, request, pk=None):
        vehicle = get_object_or_404(self.queryset, pk=pk)
        serializer = RouteSerializer(vehicle)
        return Response(response_info(status=status.HTTP_200_OK, msg="driver details", data=serializer.data))

    def update(self,request,pk=None):
        item = get_object_or_404(self.queryset, pk=pk)
        serializer = RouteSerializer(item,request.data,context={'request':request})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response({'msg': 'Data  created', 'data':serializer.data}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    def destroy(self, request,pk):
        id=pk
        stu=Route.objects.get(pk=id)
        d=stu.name
        stu.delete()
        desc=f"This Route {d} has been deleted"
        audit_log(name="Route", desc=desc, user=request.user)
        return Response(response_info(status=status.HTTP_200_OK, msg='route delete successfully',data=[]))


class ScheduleViews(viewsets.ViewSet):
    serializer_class = ScheduleSerializer
    permission_classes =  (IsAuthenticated,)
    queryset = Schedule.objects.all().order_by('-created_at')

    def create(self, request):
        serializer = ScheduleSerializer(data=request.data,context={'request':request})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(response_info(status=status.HTTP_201_CREATED, msg="schedule created successfully", data=serializer.data))
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def list(self, request):

        res = custom_paginator.paginate_queryset(self.queryset, request)

        serializer=ScheduleSerializer(res, many=True)
        return custom_paginator.get_paginated_response(serializer.data)


    vperam=OpenApiParameter(name='schedule_date',description='Schedule date',required=False,type=str,location=OpenApiParameter.QUERY)
    @extend_schema(parameters=[vperam])
    @action(detail=False, methods=['GET'])
    def schedule_out_list(self, request):
        schedule_date = request.query_params.get('schedule_date')
        if schedule_date !=None:
            s_query=Schedule.objects.filter(Q(route_id__source__icontains='Gombe') &
                                            Q(schedule_date__exact=schedule_date) ).order_by('-created_at')

        else:
            s_query=Schedule.objects.filter(route_id__source='Gombe').order_by('created_at')

        res = custom_paginator.paginate_queryset(s_query, request)

        serializer = ScheduleSerializer(res, many=True)

        return custom_paginator.get_paginated_response(grouped_schedule(serializer.data))

    vperam = OpenApiParameter(name='schedule_date', description='Schedule date', required=False, type=str,
                              location=OpenApiParameter.QUERY)

    @extend_schema(parameters=[vperam])
    @action(detail=False, methods=['GET'])
    def schedule_in_list(self, request):
        schedule_date = request.query_params.get('schedule_date')
        if schedule_date != None:
            s_query = Schedule.objects.filter(
                Q(route_id__dest__icontains='Gombe') & Q(schedule_date__exact=schedule_date)).order_by('-created_at')

        else:
            s_query = Schedule.objects.filter(route_id__dest='Gombe').order_by('created_at')

        res = custom_paginator.paginate_queryset(s_query, request)

        serializer = ScheduleSerializer(res, many=True)

        return custom_paginator.get_paginated_response(grouped_schedule(serializer.data))
    def retrieve(self, request, pk=None):
        vehicle = get_object_or_404(self.queryset, pk=pk)
        serializer = ScheduleSerializer(vehicle)
        return Response(response_info(status=status.HTTP_200_OK, msg="schedule details", data=serializer.data))

    def update(self,request,pk=None):
        item = get_object_or_404(self.queryset, pk=pk)
        serializer = ScheduleSerializer(item,request.data,context={'request':request})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response({'msg': 'Data  created', 'data':serializer.data}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    def destroy(self, request,pk):
        id=pk
        stu=Schedule.objects.get(pk=id)
        d=stu.name
        stu.delete()
        desc=f"This schedule {d} has been deleted"
        audit_log(name="Schedule", desc=desc, user=request.user)
        return Response(response_info(status=status.HTTP_200_OK, msg='schedule delete successfully',data=[]))


