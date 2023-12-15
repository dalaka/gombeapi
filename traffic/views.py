from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets, status
from rest_framework.generics import get_object_or_404
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from traffic.models import Route, Schedule
from traffic.serializer import RouteSerializer, ScheduleSerializer
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

    def list(self, request):

        res = custom_paginator.paginate_queryset(self.queryset, request)
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
        stu.delete()
        return Response(response_info(status=status.HTTP_200_OK, msg='route delete successfully',data=[]))


class ScheduleViews(viewsets.ViewSet):
    serializer_class = ScheduleSerializer
    permission_classes =  (IsAuthenticated,)
    queryset = Schedule.objects.all().order_by('created_at')

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
        stu.delete()
        return Response(response_info(status=status.HTTP_200_OK, msg='schedule delete successfully',data=[]))