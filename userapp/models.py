from django.conf import settings
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser, Group, PermissionsMixin
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.db import models
from django.utils.timezone import now
from django.utils.translation import  gettext_lazy as _
from rest_framework_simplejwt.tokens import RefreshToken


class BaseModel(models.Model):

    modified_at = models.DateTimeField(default=now)
    created_at = models.DateTimeField(default=now)
    modified_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    class Meta:
        abstract =True

class UserManager(BaseUserManager):
    """Define a model manager for User model with no username field."""

    use_in_migrations = True

    def email_validator(self, email):
        try:
            validate_email(email)
        except ValidationError:
            raise ValueError(_("Please ente a valid email address"))

    def create_user(self, username, email, phone, password, **extra_fields):
        """Create and save a User with the given email and password."""

        if not username:
            raise ValueError('The given username must be set')

        if email:
            email= self.normalize_email(email)
            self.email_validator(email)
        else:
            raise ValueError("an email address is required")
        user = self.model(username=username,email=email,phone=phone, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def _create_user(self, username,password, **extra_fields):
        """Create and save a User with the given email and password."""
        if not username:
            raise ValueError('The given username must be set')
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username,password, **extra_fields):
        """Create and save a SuperUser with the given email and password."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_verified', True)
        # extra_fields.setdefault('groups_id', 1)
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        return self._create_user(username, password, **extra_fields)


class Location(models.Model):

    name = models.CharField(max_length=50)
    code = models.CharField(max_length=50)

    def __str__(self):
        return str(self.name)

    @property
    def usercount(self):
       return User.objects.filter(location__id=self.id).count


class Department(models.Model):
    name = models.CharField(max_length=50)
    code = models.CharField(max_length=50)

    def __str__(self):
        return str(self.name)

    @property
    def usercount(self):
       return User.objects.filter(department__id=self.id).count

    def perm_set(self):
         return Group.objects.filter(department__id=self.id)

Group.add_to_class('department',models.ForeignKey(Department, on_delete=models.SET_NULL, null=True))


class User(AbstractUser, PermissionsMixin):

    location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True, verbose_name=_("Office Location"))
    department = models.ManyToManyField(Department, verbose_name=_("Department"))
    email = models.EmailField(max_length=255, verbose_name=_("Email Address"), unique=False,null=True)
    first_name = models.CharField(max_length=255, verbose_name=_("First Name"))
    last_name = models.CharField(max_length=255, verbose_name=_("Last Name"))
    phone = models.CharField(max_length=255, verbose_name=_("Phone Number"))
    modified_at = models.DateTimeField(default=now)
    created_at = models.DateTimeField(default=now)
    is_verified = models.BooleanField(default=False)










    access_code = models.CharField(max_length=255, default='customer')
    objects = UserManager()

    REQUIRED_FIELDS = ["first_name", "last_name"]
    objects = UserManager()

    def __str__(self):
        return  self.username
    @property
    def full_name(self):
        return  f"{self.first_name } {self.last_name}"

    def token(self):
        refresh=RefreshToken.for_user(self)
        return {
            'refresh':str(refresh),
            'access_token': str(refresh.access_token)
        }


class OTP(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    otp_secret = models.CharField(max_length=200)
    email = models.EmailField(unique=True)
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return self.email
