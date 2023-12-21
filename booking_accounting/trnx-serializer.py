from rest_framework import serializers

from traffic.serializer import UserTrafficSerializer
from vehicle_driver_app.models import Invoice


class InvoiceSerializer(serializers.ModelSerializer):

    created_by = UserTrafficSerializer(read_only=True)
    modified_by = UserTrafficSerializer(read_only=True)
    class Meta:
        model = Invoice
        fields =('id',  'modified_at', 'created_at', 'modified_by', 'created_by', 'loading_code', 'plate_number',
                 'sitting_capacity','driver_name','cost_per_booking','payment_status','payment_method','amount_paid','balance','charges')

        extra_kwargs = {'modified_at': {'read_only': True}, 'created_at': {'read_only': True},
                        'modified_by': {'read_only': True},'created_by': {'read_only': True},
                        'loading_code': {'read_only': True},'payment_status': {'read_only': True},
                        'expired': {'read_only': True},
                        'balance': {'read_only': True}, 'amount_paid': {'read_only': True},
                        'charges': {'read_only': True},
                        'payment_method': {'read_only': True}
                       }



    def validate(self, attrs):
        return super().validate(attrs)

    def create(self, validated_data):
        request = self.context.get('request')

        # print(sch_obj)

        user = request.user
        name = generate_activation_code("GLN")
        loading = LoadingBooking.objects.create(loading_code=name,amount_paid=0,modified_by=user, created_by=user,
                                                created_at=now(), modified_at=now(),
                                         **validated_data)
        return loading

    def update(self, instance, validated_data):
        request = self.context.get('request')
        user=request.user
        instance.plate_number = validated_data.get('plate_number', instance.plate_number)
        instance.sitting_capacity = validated_data.get('sitting_capacity', instance.sitting_capacity)
        instance.driver_name = validated_data.get('driver_name', instance.driver_name)
        instance.cost_per_booking = validated_data.get('cost_per_booking', instance.cost_per_booking)
        instance.modified_by=user
        instance.modified_at=now()
        instance.save()
        return instance

class LoadingingPaymentSerializer(serializers.ModelSerializer):
    amount = serializers.FloatField(write_only=True,required=True)
    payment_method= serializers.CharField(required=True,write_only=True)

    class Meta:
        model = LoadingBooking
        fields =('amount', 'payment_method')