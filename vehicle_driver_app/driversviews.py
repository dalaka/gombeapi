from django.shortcuts import render
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import viewsets, status

# Create your views here.
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.pagination import PageNumberPagination
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from userapp.permission_decorator import response_info
from userapp.utils import CustomPagination
from vehicle_driver_app.models import Driver,DriverLog
from vehicle_driver_app.serializer import DriverSerializer, DriverLogSerializer, ImageSerializer

custom_paginator=PageNumberPagination()
class DriverViews(viewsets.ViewSet):
    serializer_class = DriverSerializer
    permission_classes =  (IsAuthenticated,)
    queryset = Driver.objects.all().order_by('created_at')

    def create(self, request):
        serializer = DriverSerializer(data=request.data,context={'request':request})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response({'msg': '', 'data':serializer.data}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def list(self, request):

        res = custom_paginator.paginate_queryset(self.queryset, request)
        serializer=DriverSerializer(res, many=True)


        return custom_paginator.get_paginated_response(serializer.data)

    def retrieve(self, request, pk=None):
        vehicle = get_object_or_404(self.queryset, pk=pk)
        serializer = DriverSerializer(vehicle)
        return Response(response_info(status=status.HTTP_200_OK, msg="driver details", data=serializer.data))
    def update(self,request,pk=None):
        vehicle = get_object_or_404(self.queryset, pk=pk)
        serializer = DriverSerializer(vehicle,request.data,context={'request':request})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response({'msg': 'Data  created', 'data':serializer.data}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    def destroy(self, request,pk):
        id=pk
        stu=Driver.objects.get(pk=id)
        stu.delete()
        return Response(response_info(status=status.HTTP_200_OK, msg='Vehicle delete successfully',data=[]))


    userperam=OpenApiParameter(name='driver_id',description='driver id',required=True,type=int,location=OpenApiParameter.QUERY)
    @extend_schema(parameters=[userperam])
    @action(detail=False, methods=['GET'])
    def driver_history(self, request, *args, **kwargs):
        _id= request.query_params.get('driver_id', None)
        usr = DriverLog.objects.filter(driver_id=_id)

        res = custom_paginator.paginate_queryset(usr, request)
        serializer=DriverLogSerializer(res, many=True)

        return custom_paginator.get_paginated_response(serializer.data)


class UploadImageViews(APIView):
    parser_classes = [MultiPartParser, FormParser]
    permission_classes =  (IsAuthenticated,)

    userperam=OpenApiParameter(name='driver_id',description='driver id',required=True,type=int,location=OpenApiParameter.QUERY)

    @extend_schema(parameters=[userperam])
    def post(self,request,format=None):
        _id= request.query_params.get('driver_id', None)
        usr = Driver.objects.get(id=_id)

        serializer = ImageSerializer(instance=usr,data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)