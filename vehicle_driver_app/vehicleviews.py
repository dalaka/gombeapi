from django.shortcuts import render
from rest_framework import viewsets, status

# Create your views here.
from rest_framework.generics import get_object_or_404
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from userapp.permission_decorator import response_info
from vehicle_driver_app.models import Vehicle, Maintenance, VehicleRepair
from vehicle_driver_app.serializer import VehicleSerializer, MaintenanceSerializer, VehicleRepairSerializer

custom_paginator=PageNumberPagination()


class VehicleViews(viewsets.ViewSet):
    serializer_class = VehicleSerializer
    permission_classes =  (IsAuthenticated,)
    queryset = Vehicle.objects.all().order_by('created_at')

    def create(self, request):
        serializer = VehicleSerializer(data=request.data,context={'request':request})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response({'msg': 'Data  created', 'data':serializer.data}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def list(self, request, *args, **kwargs):

        res = custom_paginator.paginate_queryset(self.queryset, request)
        serializer=VehicleSerializer(res, many=True)
        return custom_paginator.get_paginated_response(serializer.data)

    def retrieve(self, request, pk=None):
        vehicle = get_object_or_404(self.queryset, pk=pk)
        serializer = VehicleSerializer(vehicle)
        return Response(response_info(status=status.HTTP_200_OK, msg="vehicle details", data=serializer.data))
    def update(self,request,pk=None):
        vehicle = get_object_or_404(self.queryset, pk=pk)
        serializer = VehicleSerializer(vehicle,request.data,context={'request':request})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response({'msg': 'Data  created', 'data':serializer.data}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    def destroy(self, request,pk):
        id=pk
        stu=Vehicle.objects.get(pk=id)
        stu.delete()
        return Response(response_info(status=status.HTTP_200_OK, msg='Vehicle delete successfully',data=[]))


class MaintenanceViews(viewsets.ViewSet):
    serializer_class = MaintenanceSerializer
    permission_classes =  (IsAuthenticated,)
    queryset = Maintenance.objects.all().order_by('created_at')

    def create(self, request):
        serializer = MaintenanceSerializer(data=request.data,context={'request':request})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(response_info(status=status.HTTP_201_CREATED, msg="maintenance detail", data=serializer.data))
        return Response(response_info(status=status.HTTP_400_BAD_REQUEST, msg="error", data=serializer.data))

    def list(self, request, *args, **kwargs):

        res = custom_paginator.paginate_queryset(self.queryset, request)
        serializer=MaintenanceSerializer(res, many=True)
        return custom_paginator.get_paginated_response(serializer.data)

    def retrieve(self, request, pk=None):
        vehicle = get_object_or_404(self.queryset, pk=pk)
        serializer = self.serializer_class(vehicle)
        return Response(response_info(status=status.HTTP_200_OK, msg="vehicle details", data=serializer.data))
    def update(self,request,pk=None):
        vehicle = get_object_or_404(self.queryset, pk=pk)
        serializer = self.serializer_class(vehicle,request.data,context={'request':request})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(
                response_info(status=status.HTTP_200_OK, msg="maintenance detail", data=serializer.data))
        return Response(response_info(status=status.HTTP_400_BAD_REQUEST, msg="error", data=serializer.data))

    def destroy(self, request,pk):
        id=pk
        stu=Maintenance.objects.get(pk=id)
        stu.delete()
        return Response(response_info(status=status.HTTP_200_OK, msg='Vehicle delete successfully',data=[]))


class RepairViews(viewsets.ViewSet):
    serializer_class = VehicleRepairSerializer
    permission_classes =  (IsAuthenticated,)
    queryset = VehicleRepair.objects.all().order_by('created_at')

    def create(self, request):
        serializer = self.serializer_class(data=request.data,context={'request':request})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(response_info(status=status.HTTP_201_CREATED, msg="repair detail", data=serializer.data))
        return Response(response_info(status=status.HTTP_400_BAD_REQUEST, msg="error", data=serializer.data))

    def list(self, request, *args, **kwargs):

        res = custom_paginator.paginate_queryset(self.queryset, request)
        serializer=self.serializer_class(res, many=True)
        return custom_paginator.get_paginated_response(serializer.data)

    def retrieve(self, request, pk=None):
        vehicle = get_object_or_404(self.queryset, pk=pk)
        serializer = self.serializer_class(vehicle)
        return Response(response_info(status=status.HTTP_200_OK, msg="repair details", data=serializer.data))

    def update(self,request,pk=None):
        repair = get_object_or_404(self.queryset, pk=pk)
        serializer = self.serializer_class(repair,request.data,context={'request':request})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(
                response_info(status=status.HTTP_200_OK, msg="repair detail", data=serializer.data))
        return Response(response_info(status=status.HTTP_400_BAD_REQUEST, msg="error", data=serializer.data))

    def destroy(self, request,pk):
        id=pk
        stu=VehicleRepair.objects.get(pk=id)
        stu.delete()
        return Response(response_info(status=status.HTTP_200_OK, msg='repair delete successfully',data=[]))