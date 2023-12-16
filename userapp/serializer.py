from django.contrib.auth import authenticate
from django.contrib.auth.models import update_last_login, Group
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from django.utils.encoding import smart_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.timezone import now
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.settings import api_settings

from userapp.models import Location, Department, User, OTP
from rest_framework_simplejwt.tokens import RefreshToken

from userapp.utils import reset_pwd_email


def createuser(data):
    password = data['password']
    user = User.objects.create(first_name=data['first_name'], last_name=data['last_name'],username=data['username'],
                                email=data['email'],phone=data['phone'], is_staff=False, is_active=True)
    user.set_password(password)
    user.save()
    return user

def get_perm(user):
    irmdpt = user.department.all()
    irmperm = user.groups.all()
    res=[]
    if irmdpt.exists():
        for i in irmdpt:
            rst = GroupSerializer(irmperm.filter(department=i.id),many=True)
            res.append({"department": i.name, "permissions":rst.data})
    return res


class GroupSerializer(serializers.ModelSerializer):

    class Meta:
        model = Group
        fields = ('id',  'name')

class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ('id','name', 'code', 'usercount')
        extra_kwargs = {'usercount': {'read_only': True}}


class DepartmentSerializer(serializers.ModelSerializer):
    #irmpermissions = GroupSerializer(many=True)
    permission = GroupSerializer(required=False, source='perm_set', many=True)
    class Meta:
        model = Department
        fields = ('id', 'name', 'code', 'usercount','permission')
        extra_kwargs = {'permission': {'read_only': True},'usercount': {'read_only': True},'irmpermissions': {'read_only': True}}


class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=100, min_length=6, write_only=True)
    password2 = serializers.CharField(max_length=100, min_length=6, write_only=True)
    class Meta:
        model =User
        fields = ['email', 'phone', 'first_name','username','last_name','password','password2']
    def validate(self, attrs):

        password = attrs.get('password')
        password2 = attrs.get('password2')
        if password != password2:
            raise serializers.ValidationError("password do not match")

        return attrs
    def create(self, validated_data):
        user = User.objects.create_user(password=validated_data['password'],first_name=validated_data['first_name'], \
                                        last_name=validated_data['last_name'],
                                        username=validated_data['username'],
                                        email=validated_data['email'],
                                        phone=validated_data['phone'],
                                        is_staff=False, is_active=True)
        return user

class VerifyOTPSerializer(serializers.ModelSerializer):
    email = serializers.CharField(max_length=100, min_length=6, write_only=True)
    otp = serializers.CharField(max_length=100, min_length=6, write_only=True)


    class Meta:
        model = OTP
        fields = ( 'otp', 'email')




class PasswordResetSerializer(serializers.Serializer):
    email = serializers.CharField(max_length=100, min_length=6, write_only=True)

    class Meta:
        model = User
        fields = ( 'email')


    def validate(self, attrs):
        email =attrs.get('email')
        if User.objects.filter(email=email).exists():
            user =User.objects.get(email=email)
            uidb64= urlsafe_base64_encode(smart_bytes(user.id))
            token= PasswordResetTokenGenerator().make_token(user)
            request=self.context.get('request')
            site_domain = get_current_site(request).domain

            relative_link=reverse('password-reset-confirm', kwargs={'uidb64':uidb64, 'token':token})
            abslink = f"http://{site_domain}{relative_link}"
            email_body=f"Hi use the link below to reset your password \n {abslink}"
            data ={
                'email_body':email_body,
                'email_subject': "Reset Your Password",
                'to_email':user.email,
                'first_name': user.first_name
            }
            res=reset_pwd_email(data=data)
            print(res)
        return super().validate(attrs)
class SetNewPasswordSerializer(serializers.Serializer):
    password = serializers.CharField(max_length=100, min_length=6, write_only=True)
    confirm_password = serializers.CharField(max_length=100, min_length=6, write_only=True)
    uidb64 = serializers.CharField( write_only=True)
    token = serializers.CharField( write_only=True)
    class Meta:
        fields = ["password", "confirm_password", "uidb64", "token"]

    def validate(self, attrs):
        token = attrs.get('token')
        uidb64 = attrs.get('uidb64')
        password= attrs.get('password')
        confirm_password = attrs.get('confirm_password')
        user_id = force_str(urlsafe_base64_decode(uidb64))
        user=User.objects.get(id=user_id)

        ck_token=PasswordResetTokenGenerator().check_token(user, token)

        if  not ck_token:
            raise AuthenticationFailed("reset link is invalid or has expired", 401)
        if password != confirm_password:
            raise AuthenticationFailed("password do not match")
        else:
            user.set_password(password)
            user.save()
            return user


class LoginSerializer(serializers.ModelSerializer):
    username = serializers.CharField(max_length=100, min_length=6, write_only=True)
    password = serializers.CharField(max_length=100, min_length=6, write_only=True)
    access_token = serializers.CharField(max_length=100, min_length=6, read_only=True)
    refresh_token = serializers.CharField(max_length=100, min_length=6, read_only=True)
    permission = serializers.JSONField(read_only=True)
    class Meta:
        model = User
        fields = ['username', 'password', 'access_token', 'refresh_token', 'permission']

    def validate(self, attrs):
        username = attrs.get('username')
        password =attrs.get("password")
        request = self.context.get('request')
        user= authenticate(request, username=username, password=password)
        if not user:
            raise AuthenticationFailed("Invalid credentials try again")
        if not user.is_verified:
            raise AuthenticationFailed("User has not been verified")
        user_token=user.token()

        return {"access_token":user_token.get("access_token"),
                "refresh_token": user_token.get("refresh"),
                "permission": get_perm(user)
                }


class LogoutUserSerializer(serializers.Serializer):
    refresh_token= serializers.CharField()


    default_error_messages = {
        'bad_token': ('Token is invalid or has expired')
    }
    def validate(self, attrs):
        self.token=attrs.get('refresh_token')
        return attrs

    def save(self, **kwargs):
        try:
            token= RefreshToken(self.token)
            token.blacklist()
        except TokenError:
            return self.fail('bad_token')

class UserSerializer(serializers.ModelSerializer):
    groups= GroupSerializer(many=True,read_only=True)
    location=LocationSerializer(read_only=True) #serializers.StringRelatedField(many=True)
    department = DepartmentSerializer(many=True,read_only=True)
    password2 = serializers.CharField(max_length=100, min_length=6, write_only=True)
    class Meta:
        model = User
        fields = ('id','username', 'email', 'password','password2', 'is_active', 'phone', 'last_login','last_name', 'first_name','groups', 'location','department','is_staff','modified_at','created_at')
        extra_kwargs = {'last_login': {'read_only': True},'is_active': {'read_only': True},'groups': {'read_only': True},
                        'password': {'write_only': True, 'min_length': 4},
                        'modified_at': {'read_only': True}, 'created_at': {'read_only': True},
                        'department': {'read_only': True}, 'is_staff': {'read_only': True}}


    def validate(self, attrs):

        password = attrs.get('password')
        password2 = attrs.get('password2')
        if password != password2:
            raise serializers.ValidationError("password do not match")

        return attrs
    def create(self, validated_data):
        user = User.objects.create_user(password=validated_data['password'],first_name=validated_data['first_name'], \
                                        last_name=validated_data['last_name'],
                                        username=validated_data['username'],
                                        email=validated_data['email'],
                                        phone=validated_data['phone'],
                                        is_staff=False, is_active=True)
        return user


class ChangePasswordSerializer(serializers.ModelSerializer):
    new_password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    confirm_password = serializers.CharField(write_only=True, required=True)
    old_password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('old_password', 'new_password', 'confirm_password')

    def validate(self, attrs):
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError({"detail": "Password fields didn't match."})

        return attrs

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError({"detail": "Old password is not correct"})
        return value

    def update(self, instance, validated_data):

        instance.set_password(validated_data['new_password'])
        instance.save()

        return instance

