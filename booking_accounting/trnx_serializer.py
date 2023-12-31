import django_filters
from django.utils.timezone import now
from rest_framework import serializers

from booking_accounting.models import LoadingBooking, Transaction, CurrentBalance, Report, Booking, AuditLog
from traffic.serializer import UserTrafficSerializer
from userapp.utils import generate_activation_code
from vehicle_driver_app.models import Invoice, VehicleRepair


class AuditLogSerializer(serializers.ModelSerializer):
    created_by = UserTrafficSerializer(read_only=True)

    class Meta:
        model = AuditLog
        fields =('id', 'created_at', 'created_by', 'audit_type', 'audit_description')




class VehicleRepairReportSerializer(serializers.ModelSerializer):
    created_by = UserTrafficSerializer(read_only=True)
    modified_by = UserTrafficSerializer(read_only=True)
    class Meta:
        model = VehicleRepair
        fields =('id',  'modified_at', 'created_at', 'modified_by', 'created_by', 'vehicle_id', 'repair_date',
                 'repair_descriptions', 'repair_cost', 'repair_code')


class BookingReportSerializer(serializers.ModelSerializer):

    created_by = UserTrafficSerializer(read_only=True)
    modified_by = UserTrafficSerializer(read_only=True)
    class Meta:
        model = Booking
        fields =('id',  'modified_at', 'created_at', 'modified_by', 'created_by', 'passenger_full_name', 'booking_code',
                 'seat_no','passenger_phone','nk_full_name','nk_contact','relationship', 'price',
                 'payment_status','payment_method','destination', 'expired', 'balance', 'amount_paid',
                 'source')

class ReportSerializer(serializers.ModelSerializer):


    class Meta:
        model = Report
        fields =('id',  'start', 'created_at', 'end', 'report_type', 'total','data')
        read_only_fields = ['total', 'created_at', 'data']

    def validate(self, attrs):
        return super().validate(attrs)

    def create(self, validated_data):
        request = self.context.get('request')



        user = request.user
        name = generate_activation_code("GIN")
        loading =Invoice.objects.create(invoiceId=name,amount_paid=0,modified_by=user, created_by=user,**validated_data)
        return loading


class BalanceSerializer(serializers.ModelSerializer):


    class Meta:
        model = CurrentBalance
        fields =('current_total_income', 'current_total_expense', 'profit')



class InvoiceFilter(django_filters.FilterSet):
    created_at = django_filters.DateFilter(field_name='created_at__date', lookup_expr="exact")
    created_by = django_filters.NumberFilter(field_name='created_by__id', lookup_expr="exact")
    class Meta:
        model = Invoice
        fields = ['created_at', 'is_approved', 'created_by']

class InvoiceSerializer(serializers.ModelSerializer):

    created_by = UserTrafficSerializer(read_only=True)
    modified_by = UserTrafficSerializer(read_only=True)
    class Meta:
        model = Invoice
        fields =('id',  'modified_at', 'created_at', 'modified_by', 'created_by', 'invoiceId', 'purpose',
                 'description','receiver_name','balance','invoice_status','payment_method','amount_paid',
                 'balance','invoice_total', 'approved_by', 'is_approved', 'receiver_name')

        extra_kwargs = {'modified_at': {'read_only': True}, 'created_at': {'read_only': True},
                        'modified_by': {'read_only': True},'created_by': {'read_only': True},
                        'invoiceId': {'read_only': True},'invoice_status': {'read_only': True},
                        'approved_by': {'read_only': True},
                        'balance': {'read_only': True}, 'amount_paid': {'read_only': True},
                        'payment_method': {'read_only': True}
                       }


    def validate(self, attrs):
        return super().validate(attrs)

    def create(self, validated_data):
        request = self.context.get('request')

        # print(sch_obj)

        user = request.user
        name = generate_activation_code("GIN")
        loading =Invoice.objects.create(invoiceId=name,amount_paid=0,modified_by=user, created_by=user,**validated_data)
        return loading

    def update(self, instance, validated_data):
        request = self.context.get('request')
        user=request.user
        instance.description = validated_data.get('description', instance.description)
        instance.receiver_name = validated_data.get('receiver_name', instance.receiver_name)
        instance.invoice_total = validated_data.get('invoice_total', instance.invoice_total)
        instance.modified_by=user
        instance.modified_at=now()
        instance.save()
        return instance

class InvoicePaymentSerializer(serializers.ModelSerializer):
    amount = serializers.FloatField(write_only=True,required=True)
    payment_method= serializers.CharField(required=True,write_only=True)
    receiver_name= serializers.CharField(required=True,write_only=True)
    is_approved = serializers.BooleanField(default=False, write_only=True)

    class Meta:
        model = LoadingBooking
        fields =('amount', 'payment_method', 'receiver_name', 'is_approved')


class TransactionSerializer(serializers.ModelSerializer):

    created_by = UserTrafficSerializer(read_only=True)
    modified_by = UserTrafficSerializer(read_only=True)
    class Meta:
        model = Transaction
        fields =('id',  'modified_at', 'created_at', 'modified_by', 'created_by', 'transactionId', 'orderId',
                 'description','trans_method','amount_paid',
                 'payment_method')

