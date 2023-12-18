from django.utils.timezone import now
from rest_framework import serializers

from booking_accounting.models import Booking, Transaction
from traffic.models import Schedule
from traffic.serializer import UserTrafficSerializer
from userapp.utils import generate_activation_code

def transction(user,orderid,price,des,paymet_method,trnx_method):
    Transaction.objects.create(transactionId=generate_activation_code('T'),created_at=now(),modified_at=now(),
                               created_by=user, modified_by=user,
                               orderId=orderid,amount_paid=price,description=des,payment_method=paymet_method,
                               trans_method=trnx_method)
    return True
class BookingSerializer(serializers.ModelSerializer):
    #driver = ScheduleSerializer(read_only=True,source='from_g', required=False)

    created_by = UserTrafficSerializer(read_only=True)
    modified_by = UserTrafficSerializer(read_only=True)
    class Meta:
        model = Booking
        fields =('id',  'modified_at', 'created_at', 'modified_by', 'created_by', 'passenger_full_name', 'booking_code',
                 'seat_no','passenger_phone','nk_full_name','nk_contact','relationship','schedule_id', 'price',
                 'payment_status','payment_method')

        extra_kwargs = {'modified_at': {'read_only': True}, 'created_at': {'read_only': True},
                        'modified_by': {'read_only': True},'created_by': {'read_only': True},
                        'booking_code': {'read_only': True},
                        'price': {'read_only': True},'payment_status': {'read_only': True}
                       }

    def validate(self, attrs):
        return super().validate(attrs)


    def create(self, validated_data,):
        request = self.context.get('request')
        sch_obj = self.context.get('obj')
        seat_no = validated_data.get('seat_no')
        seats=sch_obj.seats
        no=sch_obj.seats_available
        #print(sch_obj)


        user=request.user
        name=generate_activation_code("GBN")
        booking=Booking.objects.create(price=sch_obj.price,payment_status='paid',booking_date=sch_obj.schedule_date,
                                       booking_code=name,
                                       modified_by=user,created_by=user,created_at=now(),modified_at=now(),
                                       **validated_data )
        for s in seats:
            #print(s)
            if s['seat_number'] == seat_no and s['is_available'] == True:
                s['is_available'] = False

        sch_obj.seats = seats
        sch_obj.seats_available = no - 1
        sch_obj.save()
        transction(user=user,orderid=booking.booking_code,price=booking.price,des='Booking',
                   paymet_method=booking.payment_method,trnx_method='Credit')
        return booking
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
