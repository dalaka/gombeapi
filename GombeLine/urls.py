"""
URL configuration for GombeLine project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

from GombeLine import dev

urlpatterns = [
    path('apidoc/', SpectacularAPIView.as_view(), name='schema'),
    path('api/swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    path('admin/', admin.site.urls),
    path('account/', include('userapp.acount-urls')),
    path('office/', include('userapp.location-urls')),
    path('department/', include('userapp.department-urls')),
    path('vehicle/', include('vehicle_driver_app.vehicle-urls')),
    path('driver/', include('vehicle_driver_app.driverurls')),
    path('item/', include('vehicle_driver_app.itemurls')),
    path('maintenance/', include('vehicle_driver_app.maintenceurls')),
    path('repair/', include('vehicle_driver_app.repairurls')),
    path('route/', include('traffic.route-url')),
    path('schedule/', include('traffic.schedule-urls')),
    path('booking/', include('booking_accounting.booking-urls')),
    path('loading/', include('booking_accounting.loading-urls')),
    path('invoice/', include('booking_accounting.tranx-urls')),
]+ static(dev.MEDIA_URL, document_root=dev.MEDIA_ROOT)

