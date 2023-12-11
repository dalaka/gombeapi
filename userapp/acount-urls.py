from django.urls import path, include
from rest_framework import routers
from rest_framework_simplejwt.views import TokenRefreshView, TokenObtainPairView

from userapp.views import AllGroupView, UserView, LocationView, DepartmentView, RegisterUserView, VerifyEmailView, \
    LoginUserView, ResetPwdView, SetNewPasswordView, PasswordResetConfirmView, LogoutView

router = routers.DefaultRouter()

router.register('',  UserView,'user')

urlpatterns = [

    path('api/v1/', include(router.urls)),
    path('api/v1/register/', RegisterUserView.as_view(), name="reqister" ),
    path('api/v1/verify-email/', VerifyEmailView.as_view(), name="verify-email"),
    path('api/v1/login', LoginUserView.as_view(), name='login'),
    path('api/v1/logout', LogoutView.as_view(), name='logout'),
    path('api/v1/password-reset',ResetPwdView.as_view(), name='password-reset'),
    path('api/v1/password-reset-confirm/<uidb64>/<token>', PasswordResetConfirmView.as_view(), name='password-reset-confirm'),
    path('api/v1/set-new-password',SetNewPasswordView.as_view(), name='set-new-password'),
    path('api/v1/refresh-token/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/v1/permission/', AllGroupView.as_view(), name='token_refresh'),
]