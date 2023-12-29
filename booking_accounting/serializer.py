import django_filters
from django.utils.timezone import now
from rest_framework import serializers

from booking_accounting.models import Booking, Transaction, CurrentBalance
from booking_accounting.util import create_invoice, audit_log
from traffic.models import Schedule
from traffic.serializer import UserTrafficSerializer, ScheduleSerializer
from userapp.utils import generate_activation_code
from vehicle_driver_app.models import Approval


def transction(user,orderid,price,des,paymet_method,trnx_method):
    Transaction.objects.create(transactionId=generate_activation_code('T'),created_at=now(),modified_at=now(),
                               created_by=user, modified_by=user,
                               orderId=orderid,amount_paid=price,description=des,payment_method=paymet_method,
                               trans_method=trnx_method)
    try:
        bal = CurrentBalance.objects.get(name='pay')
        if trnx_method =='Credit':
            bal.current_total_income +=price
        else:
            bal.current_total_expense +=price
        bal.save()
        return True
    except CurrentBalance.DoesNotExist:
        if trnx_method == 'Credit':
            CurrentBalance.objects.create(name='pay',current_total_expense=0,current_total_income=price)
        else:
            CurrentBalance.objects.create(name='pay', current_total_expense=price, current_total_income=0)
        return True

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

class ScheduleDetailSerializer(serializers.ModelSerializer):

    driver = DriverDetailSerializer(read_only=True,source='driver_detail', required=False)
    vehicle = VehicleDetailSerializer(required=False, source='vehicle_detail',read_only=True)

    class Meta:
        model = Schedule
        fields =( 'driver', 'vehicle','schedule_date', 'depart_time')

class BookingChangeSerializer(serializers.ModelSerializer):
    route_changed = serializers.BooleanField(write_only=True)
    schedule_detail = ScheduleDetailSerializer(read_only=True,source='s_detail', required=False)

    created_by = UserTrafficSerializer(read_only=True)
    modified_by = UserTrafficSerializer(read_only=True)
    class Meta:
        model = Booking
        fields =('id',  'modified_at', 'created_at', 'modified_by', 'created_by', 'passenger_full_name', 'booking_code',
                 'seat_no','passenger_phone','nk_full_name','nk_contact','relationship','schedule_id', 'price',
                 'payment_status','payment_method','destination', 'expired','amount_paid','route_changed','balance',
                 'schedule_detail','source')

        extra_kwargs = {'modified_at': {'read_only': True}, 'created_at': {'read_only': True},
                        'modified_by': {'read_only': True},'created_by': {'read_only': True},
                        'booking_code': {'read_only': True},
                        'price': {'read_only': True},'payment_status': {'read_only': True},
                        'destination': {'read_only': True}, 'passenger_full_name': {'read_only': True},
                        'passenger_phone': {'read_only': True}, 'nk_full_name': {'read_only': True},
                        'nk_contact': {'read_only': True}, 'relationship': {'read_only': True},
                        'expired': {'read_only': True}, 'balance': {'read_only': True},
                        'amount_paid': {'read_only': True},'payment_method': {'read_only': True},
                       'schedule_id': {'read_only': True}, 'schedule_detail': {'read_only': True},
                        'source': {'read_only': True}}

    def validate(self, attrs):
        return super().validate(attrs)


    def update(self, instance,validated_data):
        request = self.context.get('request')
        sch_obj = self.context.get('obj')
        old_sch = self.context.get('old')
        route_changed = validated_data.pop('route_changed')
        seats=sch_obj.seats
        no=sch_obj.seats_available
        seat_no=validated_data.pop('seat_no')
        #print(sch_obj)
        user=request.user
        for s in seats:
            #print(s)
            if s['seat_number'] == seat_no and s['is_available'] == True:
                s['is_available'] = False

        sch_obj.seats = seats
        sch_obj.seats_available = no - 1
        sch_obj.save()
        n=f"Bus Changed from {old_sch.vehicle_id.custom_naming} to {sch_obj.vehicle_id.custom_naming} "


        if route_changed:
            instance.seat_no=seat_no
            instance.price = sch_obj.price
            instance.destination = sch_obj.route_id.dest
            instance.source = sch_obj.route_id.source
            instance.schedule_id = sch_obj
            instance.modified_by = user
            instance.modified_at = now()
            instance.save()

            #approve = create_invoice(purpose=instance.booking_code, description=n,total=instance.balance['change']
        else:
            instance.seat_no=seat_no
            instance.schedule_id = sch_obj
            instance.modified_by = user
            instance.modified_at = now()
            instance.save()
        desc=f"{n} with booking code {instance.booking_code} "
        audit_log(name="Booking", desc=desc, user=user)
        return instance
class BookingFilter(django_filters.FilterSet):
    created_at = django_filters.DateFilter(field_name='created_at__date', lookup_expr="exact")
    created_by = django_filters.NumberFilter(field_name='created_by__id', lookup_expr="exact")
    booking_date = django_filters.DateFilter(field_name='booking_date', lookup_expr="exact")
    vehicle_id = django_filters.NumberFilter(field_name='schedule_id__vehicle_id_id' , lookup_expr="exact")
    driver_id = django_filters.NumberFilter(field_name='schedule_id__driver_id_id' , lookup_expr="exact")

    route_id = django_filters.NumberFilter(field_name='schedule_id__route_id_id', lookup_expr="exact")

    class Meta:
        model = Booking
        fields = ['created_at', 'booking_date', 'created_by']




class BookingSerializer(serializers.ModelSerializer):
    schedule_detail = ScheduleDetailSerializer(read_only=True,source='s_detail', required=False)

    created_by = UserTrafficSerializer(read_only=True)
    modified_by = UserTrafficSerializer(read_only=True)
    class Meta:
        model = Booking
        fields =('id',  'modified_at', 'created_at', 'modified_by', 'created_by', 'passenger_full_name', 'booking_code',
                 'seat_no','passenger_phone','nk_full_name','nk_contact','relationship','schedule_id', 'price',
                 'payment_status','payment_method','destination', 'expired', 'balance', 'amount_paid', 'schedule_detail',
                 'source')

        extra_kwargs = {'modified_at': {'read_only': True}, 'created_at': {'read_only': True},
                        'modified_by': {'read_only': True},'created_by': {'read_only': True},
                        'booking_code': {'read_only': True},
                        'price': {'read_only': True},'payment_status': {'read_only': True},
                        'destination': {'read_only': True},'expired': {'read_only': True},
                        'balance': {'read_only': True}, 'amount_paid': {'read_only': True},
                        'schedule_detail': {'read_only': True},'source': {'read_only': True}
                       }

    def validate(self, attrs):
        return super().validate(attrs)

    def create(self, validated_data):
        request = self.context.get('request')
        sch_obj = self.context.get('obj')
        seat_no = validated_data.get('seat_no')
        seats = sch_obj.seats
        no = sch_obj.seats_available
        # print(sch_obj)

        user = request.user
        name = generate_activation_code("GBN")
        booking = Booking.objects.create(price=sch_obj.price,amount_paid=0, booking_date=sch_obj.schedule_date,
                                         booking_code=name, destination=sch_obj.route_id.dest,source=sch_obj.route_id.source,
                                         modified_by=user, created_by=user, created_at=now(), modified_at=now(),
                                         **validated_data)
        for s in seats:
            # print(s)
            if s['seat_number'] == seat_no and s['is_available'] == True:
                s['is_available'] = False

        sch_obj.seats = seats
        sch_obj.seats_available = no - 1
        sch_obj.save()


        return booking

    def update(self, instance, validated_data):
        request = self.context.get('request')
        user=request.user
        instance.passenger_full_name = validated_data.get('passenger_full_name', instance.passenger_full_name)
        instance.passenger_phone = validated_data.get('passenger_phone', instance.passenger_phone)
        instance.nk_full_name = validated_data.get('nk_full_name', instance.nk_full_name)
        instance.nk_contact = validated_data.get('nk_contact', instance.nk_contact)
        instance.relationship = validated_data.get('relationship', instance.relationship)
        instance.modified_by=user
        instance.modified_at=now()
        instance.save()
        desc=f"Update was done on the this booking {instance.booking_code}"
        audit_log(name="Book",desc=desc,user=user)
        return instance



class BookingPaymentSerializer(serializers.ModelSerializer):
    amount = serializers.FloatField(write_only=True,required=True)
    payment_method= serializers.CharField(required=True,write_only=True)

    class Meta:
        model = Booking
        fields =('amount', 'payment_method')