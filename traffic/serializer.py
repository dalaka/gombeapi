from django.utils.timezone import now
from rest_framework import serializers

from traffic.models import Route, Schedule
from traffic.utils import gen_seat
from vehicle_driver_app.models import DriverLog


class RouteSerializer(serializers.ModelSerializer):

    class Meta:
        model = Route
        fields =('id',  'modified_at', 'created_at', 'modified_by', 'created_by', 'name', 'source','dest')

        extra_kwargs = {'modified_at': {'read_only': True}, 'created_at': {'read_only': True},
                        'modified_by': {'read_only': True},'created_by': {'read_only': True},
                        'name': {'read_only': True}
                       }

    def validate(self, attrs):
        return super().validate(attrs)


    def create(self, validated_data,):
        request = self.context.get('request')
        user=request.user
        name=f"{validated_data.get('source')}-{validated_data.get('dest')}"
        return Route.objects.create(name=name,modified_by=user,created_by=user,created_at=now(),modified_at=now(),**validated_data )

    def update(self, instance, validated_data):
        request = self.context.get('request')
        user=request.user
        instance.name = f"{validated_data.get('source', instance.source)}-{validated_data.get('dest', instance.dest)}"
        instance.source = validated_data.get('source', instance.source)
        instance.dest = validated_data.get('dest', instance.dest)
        instance.modified_by=user
        instance.modified_at=now()
        instance.save()
        return instance

class VehicleDetailSerializer(serializers.ModelSerializer):



    class Meta:
        from vehicle_driver_app.models import Vehicle
        model = Vehicle
        fields =('id','vehicle_make', 'vehicle_model','vin', 'reg_number', 'vehicle_type', 'color','sitting_capacity',
                 'custom_naming','vehicle_condition','is_available')
class DriverDetailSerializer(serializers.ModelSerializer):

    class Meta:
        from vehicle_driver_app.models import  Driver
        model = Driver
        fields =('id', 'first_name', 'address','last_name', 'phone', 'address', 'driver_license','nk_full_name','nk_contact',
                 'relationship','nk_address','expiry_date', 'number_trips','is_license_active','driver_number')

class ScheduleSerializer(serializers.ModelSerializer):
    driver = DriverDetailSerializer(read_only=True,source='driver_detail', required=False)

    vehicle = VehicleDetailSerializer(required=False, source='vehicle_detail',read_only=True)

    class Meta:
        model = Schedule
        fields =('id',  'modified_at', 'created_at', 'modified_by', 'created_by', 'name', 'route_id','driver_id',
                 'price', 'seats', 'schedule_date', 'seats_available', 'vehicle_id','driver', 'vehicle')

        extra_kwargs = {'modified_at': {'read_only': True}, 'created_at': {'read_only': True},
                        'modified_by': {'read_only': True},'created_by': {'read_only': True},
                        'name': {'read_only': True}, 'seats': {'read_only': True},
                        'seats_available': {'read_only': True},'vehicle_id': {'write_only': True},
                        'vehicle': {'read_only': True}, 'driver_id': {'write_only': True},
                        'driver': {'read_only': True}
                       }


    def validate(self, attrs):

        sch=Schedule.objects.filter(driver_id=attrs['driver_id'], route_id=attrs['route_id'],
                                schedule_date=attrs['schedule_date']).exists()
        if sch:
            raise serializers.ValidationError("Driver has already been register on this route")
        return super().validate(attrs)


    def create(self, validated_data,):
        request = self.context.get('request')
        user=request.user
        driverid = validated_data.pop('driver_id')
        vehicleid = validated_data.pop('vehicle_id')
        routeid = validated_data.pop('route_id')
        schedule=Schedule.objects.create(modified_by=user,created_by=user,created_at=now(),modified_at=now(),
                                       driver_id=driverid,vehicle_id=vehicleid,route_id=routeid,
                                       seats_available=int(vehicleid.sitting_capacity),
                                       seats=gen_seat(int(vehicleid.sitting_capacity)),**validated_data )
        DriverLog.objects.create(datetime_daparture=schedule.schedule_date,driver_id=driverid,departure=routeid.source, destination=routeid.dest)
        return schedule

    def update(self, instance, validated_data):
        request = self.context.get('request')
        user=request.user
        instance.name = validated_data.get('name', instance.name)
        instance.route_id = validated_data.get('route_id', instance.route_id)
        instance.driver_id = validated_data.get('driver_id', instance.driver_id)
        instance.vehicle_id = validated_data.get('vehicle_id', instance.vehicle_id)
        instance.price = validated_data.get('price', instance.price)
        instance.modified_by=user
        instance.modified_at=now()
        instance.save()
        return instance
