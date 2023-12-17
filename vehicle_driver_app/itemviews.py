from django.db.models import Q
from django.shortcuts import render
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import viewsets, status

# Create your views here.
from rest_framework.generics import get_object_or_404
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from userapp.permission_decorator import response_info
from userapp.utils import CustomPagination
from vehicle_driver_app.models import Driver, DriverLog, Item
from vehicle_driver_app.serializer import ItemsSerializer
custom_paginator=PageNumberPagination()

class ItemViews(viewsets.ViewSet):
    serializer_class = ItemsSerializer
    permission_classes =  (IsAuthenticated,)
    queryset = Item.objects.all().order_by('created_at')

    def create(self, request):
        serializer = ItemsSerializer(data=request.data,context={'request':request})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response({'msg': '', 'data':serializer.data}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    vperam=OpenApiParameter(name='search',description='search Item',required=False,type=str,location=OpenApiParameter.QUERY)
    @extend_schema(parameters=[vperam])
    def list(self, request):
        search = request.query_params.get('search')
        if search !=None:
            i_query = Item.objects.filter(Q(name__icontains=search)).order_by('created_at')
        else:
            i_query =self.queryset
        res = custom_paginator.paginate_queryset(i_query, request)
        serializer=ItemsSerializer(res, many=True)
        return custom_paginator.get_paginated_response(serializer.data)

    def retrieve(self, request, pk=None):
        vehicle = get_object_or_404(self.queryset, pk=pk)
        serializer = ItemsSerializer(vehicle)
        return Response(response_info(status=status.HTTP_200_OK, msg="driver details", data=serializer.data))

    def update(self,request,pk=None):
        item = get_object_or_404(self.queryset, pk=pk)
        serializer = ItemsSerializer(item,request.data,context={'request':request})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response({'msg': 'Data  created', 'data':serializer.data}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    def destroy(self, request,pk):
        id=pk
        stu=Item.objects.get(pk=id)
        stu.delete()
        return Response(response_info(status=status.HTTP_200_OK, msg='item delete successfully',data=[]))