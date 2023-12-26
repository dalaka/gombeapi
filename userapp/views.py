import pyotp
from django.contrib.auth.models import Group
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import smart_str, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_decode
from django.utils.timezone import now
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import status, viewsets, generics
from rest_framework.decorators import action
from rest_framework.generics import GenericAPIView, get_object_or_404
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from userapp.models import User, Location, Department, OTP
from userapp.permission_decorator import has_permission, response_info
from userapp.serializer import GroupSerializer, UserSerializer, createuser, LocationSerializer, DepartmentSerializer, \
    ChangePasswordSerializer, UserRegisterSerializer, VerifyOTPSerializer, LoginSerializer, PasswordResetSerializer, \
    SetNewPasswordSerializer, LogoutUserSerializer
from userapp.utils import send_code_to_user

paginator = PageNumberPagination()


class RegisterUserView(GenericAPIView):
    serializer_class = UserRegisterSerializer

    def post(self, request):
        user_data = request.data
        serializer = self.serializer_class(data=user_data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            user=serializer.data
            #send email
            send_code_to_user(user['email'])
            f= User.objects.get(email=user['email'])
            return Response(
                response_info(status=status.HTTP_201_CREATED, \
                              msg=f"Hi {f.first_name} thanks for signing up a passcode has been sent to your email",\
                              data=user
            ))
        return Response(response_info(status=status.HTTP_400_BAD_REQUEST, msg=serializer.errors,data=[]))

class VerifyEmailView(GenericAPIView):
    serializer_class =  VerifyOTPSerializer

    def post(self,request):
        otp_code = request.data.get('otp')
        email = request.data.get('email')
        try:
            user_code_obj = OTP.objects.get(email=email)
            user = User.objects.get(id=user_code_obj.user.id)

            otp = pyotp.TOTP(user_code_obj.otp_secret,interval=300)
            otp_status = otp.verify(otp_code)
            print(otp_status)
            if otp_status:
                if user_code_obj.user.is_verified:
                    return Response(
                        response_info(status=status.HTTP_401_UNAUTHORIZED,
                                      msg="Account has already been verified successfully", data=[]))

                user.is_verified =True
                user.save()
                return Response(response_info(status=status.HTTP_200_OK,msg="Account has been verified successfully", data=[]))

            return Response(response_info(status=status.HTTP_403_FORBIDDEN, msg="OTP has expired", data=[]))
        except OTP.DoesNotExist:
            return Response(response_info(status=status.HTTP_404_NOT_FOUND, msg="OTP does not exist", data=[]))

class LoginUserView(GenericAPIView):
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data, context={'request':request})
        serializer.is_valid(raise_exception=True)
        return Response(response_info(status=status.HTTP_200_OK, msg="Login successfully", data=serializer.data))

class ResetPwdView(GenericAPIView):
    serializer_class = PasswordResetSerializer
    def post(self,request):
        serializer= self.serializer_class(data=request.data, context={'request':request})
        serializer.is_valid(raise_exception=True)
        msg="A link has been sent to your email to reset your password"
        return Response(response_info(status=status.HTTP_200_OK, msg=msg, data=[]))


class SetNewPasswordView(GenericAPIView):
    serializer_class = SetNewPasswordSerializer
    def patch(self, request):
        serializer = self.serializer_class(data=request.data,context={'request':request} )
        serializer.is_valid(raise_exception=True)
        return Response(response_info(status=status.HTTP_200_OK, msg="Password reset successfully", data=[]))


class PasswordResetConfirmView(GenericAPIView):
    def get(self, request, uidb64, token):
        try:
            user_id= smart_str(urlsafe_base64_decode(uidb64))
            user= User.objects.get(id=user_id)
            if not PasswordResetTokenGenerator().check_token(user,token):
                return Response(response_info(status=status.HTTP_401_UNAUTHORIZED, msg='Token is invalid or expires',
                                             data=[]))
            data={ "uidb64":uidb64, "token":token}

            return  Response(response_info(status=status.HTTP_200_OK, msg="credential is correct", data=data))
        except DjangoUnicodeDecodeError:
            msg="Token is invalid or hsd expired"
            return Response(response_info(status=status.HTTP_401_UNAUTHORIZED,msg=msg, data=[] ))


class AllGroupView(APIView):
    """ This  end point allows user to get permission by department ID"""

    serializer_class =GroupSerializer
    permission_classes = (IsAuthenticated,)
    peram=OpenApiParameter(name='id',description='department id',required=True,type=int,location=OpenApiParameter.QUERY)
    @extend_schema(parameters=[peram])
    @has_permission([{"grp":'Admin',"perm":['admin']}])
    def get(self,request):
        _id = request.query_params.get('id', None)
        queryset = Group.objects.filter(department__id=_id)
        serial = GroupSerializer(queryset,many=True)
        return Response(response_info(status=status.HTTP_200_OK,msg='Permission list',data=serial.data))


class LogoutView(GenericAPIView):
    serializer_class = LogoutUserSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class UserView(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = UserSerializer


    def get_queryset(self):
        obj = User.objects.all().order_by('created_at')
        return obj

    def create(self, request, *args, **kwargs):
        " Create User endpoint"
        usr=User.objects.filter(username=request.data['username'])

        usr1=User.objects.filter(email=request.data['email'])
        if usr.exists() ==True:
            return Response(response_info(status=status.HTTP_404_NOT_FOUND,msg="username has already been registered",
                                          data=[]))
        if usr1.exists() == True:
            return Response(response_info(status=status.HTTP_404_NOT_FOUND, msg="Phone number has already been registered",
                              data=[]))
        else:
            res=createuser(request.data)
            serialiseduser=UserSerializer(res)
            return Response(response_info(status=status.HTTP_201_CREATED,msg="New user has been created successfully",
                                          data=serialiseduser.data))

    def update(self, request, *args, **kwargs):
        """Update user endpoint"""
        user_object = self.get_object()
        user_object.email = request.data.get('email', user_object.email)
        user_object.first_name = request.data.get("first_name", user_object.first_name)
        user_object.last_name = request.data.get("last_name",user_object.last_name)
        user_object.is_active =request.data.get("is_active",user_object.is_active)
        user_object.phone =request.data.get("phone",user_object.phone)
        user_object.modified_at = now()
        user_object.save()
        user_object.location = Location.objects.get(id=request.data["location"])
        user_object.save()
        user_object.groups.clear()
        user_object.department.clear()
        for i in request.data["groups"]["department"]:
            user_object.department.add(i)
        for j in request.data["groups"]["perm"]:
            user_object.groups.add(j)
        serializer = UserSerializer(user_object)
        return Response(response_info(status=status.HTTP_200_OK,msg="updated successfully",data=serializer.data))

    def destroy(self, request, *args, **kwargs):
        user= self.get_object()
        if self.request.user.is_superuser !=True:
            return Response(response_info(status=status.HTTP_403_FORBIDDEN, msg="You are not a super user",data=[]))
        if user.is_superuser ==True:
            return Response(response_info(status=status.HTTP_403_FORBIDDEN, msg="You can not delete a super user",data=[]))
        if user:
            user.delete()
            return Response(response_info(status=status.HTTP_200_OK, msg="The user deleted successfully",data=[]))
        else:
            return Response(response_info(status=status.HTTP_400_BAD_REQUEST, msg="User not found",data=[]))


    userperam=OpenApiParameter(name='user_id',description='user id',required=True,type=int,location=OpenApiParameter.QUERY)
    @extend_schema(parameters=[userperam])
    @action(detail=False, methods=['GET'])
    def activate_deactivate(self, request, *args, **kwargs):
        _id= request.query_params.get('user_id', None)
        usr = User.objects.filter(id=_id)

        if usr.exists():
            res = User.objects.get(id=_id)
            if res.is_active ==True:
                res.is_active=False
                res.save()
                return Response(response_info(status=status.HTTP_200_OK,msg= "user has been deactivated successfully", data=[]))
            else:
                res.is_active=True
                res.save()
                return Response(response_info(status=status.HTTP_200_OK,msg= "user has been activated successfully", data=[]))
        else:
            return Response(response_info(status=status.HTTP_404_NOT_FOUND,msg= "user not found", data=[]))

class LocationView(viewsets.ModelViewSet):
    serializer_class = LocationSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):

        return Location.objects.all()

    def create(self, request, *args, **kwargs):
        if Location.objects.filter(code=request.data['code']).exists():
            return Response(response_info(status=status.HTTP_400_BAD_REQUEST,msg='code already exist',data=[]))
        res = Location.objects.create(name=request.data['name'],code= request.data['code'])
        obj = LocationSerializer(res)
        return Response(response_info(status=status.HTTP_200_OK,msg='location lists',data=obj.data))

    def list(self, request, *args, **kwargs):
        res = paginator.paginate_queryset(self.get_queryset(), request, view=None)

        serializer=LocationSerializer(res, many=True)
        return paginator.get_paginated_response(serializer.data)

class DepartmentView(viewsets.ModelViewSet):
    serializer_class = DepartmentSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):

        return Department.objects.all()

    def create(self, request, *args, **kwargs):
        if Department.objects.filter(code=request.data['code']).exists():
            return Response({"detail":'code already exist'}, status=status.HTTP_400_BAD_REQUEST)
        res = Department.objects.create(name=request.data['name'],code= request.data['code'])
        obj = DepartmentSerializer(res)
        return Response(obj.data)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

class ChangePasswordView(viewsets.ViewSet):
    permission_classes = (IsAuthenticated,)

    queryset = User.objects.all()
    permission_classes = (IsAuthenticated,)
    serializer_class = ChangePasswordSerializer

    def update(self,request,pk=None):
        item = get_object_or_404(self.queryset, pk=pk)
        serializer = self.serializer_class(item,request.data,context={'request':request})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response({'msg': 'Data  created', 'data':serializer.data}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
