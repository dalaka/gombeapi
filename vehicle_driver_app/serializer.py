from django.utils.timezone import now
from rest_framework import serializers

from booking_accounting.util import create_invoice
from userapp.models import User
from userapp.utils import generate_activation_code
from vehicle_driver_app.models import Vehicle, Driver, DriverLog, Maintenance, VehicleRepair, Item, Approval

class VehicleDetailSerializer(serializers.ModelSerializer):

    class Meta:
        model = Vehicle
        fields =('id', 'vehicle_make', 'vehicle_model',
                 'vin', 'reg_number', 'vehicle_type', 'color','sitting_capacity','custom_naming','vehicle_condition',
                 'is_available')

class UserDetailSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('id','last_name', 'first_name')



class ImageSerializer(serializers.ModelSerializer):

    class Meta:
        model = Driver
        fields = ["image"]

    def update(self, instance, validated_data):

        instance.image = validated_data.get('image', instance.image)
        instance.save()
        return instance

class DriverLogSerializer(serializers.ModelSerializer):

    class Meta:
        model = DriverLog
        fields =('id', 'driver_id', 'departure',
                 'destination', 'datetime_daparture', 'datetime_destination','vehicle_name', 'is_arrived')

        extra_kwargs = {'is_arrived': {'read_only': True}}

class ItemsSerializer(serializers.ModelSerializer):

    class Meta:
        model = Item
        fields =('id',  'modified_at', 'created_at', 'modified_by', 'created_by', 'name', 'quantity',
                 'isavailable')

        extra_kwargs = {'modified_at': {'read_only': True}, 'created_at': {'read_only': True},
                        'modified_by': {'read_only': True},'created_by': {'read_only': True},
                        'isavailable': {'read_only': True}
                       }

    def validate(self, attrs):
        return super().validate(attrs)


    def create(self, validated_data,):
        request = self.context.get('request')
        user=request.user
        return Item.objects.create(modified_by=user,created_by=user,created_at=now(),modified_at=now(),**validated_data )

    def update(self, instance, validated_data):
        request = self.context.get('request')
        user=request.user
        instance.name = validated_data.get('name', instance.name)
        instance.quantity = validated_data.get('quantity', instance.quantity)
        instance.modified_by=user
        instance.modified_at=now()
        instance.save()
        return instance

class MaintenanceSerializer(serializers.ModelSerializer):
    maintenance_type = ItemsSerializer(many=True, read_only=True)
    item_ids= serializers.JSONField(default=[],write_only=True)
    created_by = UserDetailSerializer(read_only=True)
    modified_by = UserDetailSerializer(read_only=True)
    vehicle_detail = VehicleDetailSerializer(read_only=True,source='vehicle_d')

    class Meta:
        model = Maintenance
        fields =('id',  'modified_at', 'created_at', 'modified_by', 'created_by', 'vehicle_id', 'maintenance_date',
                 'due_date', 'maintenance_type', 'maintenance_cost', 'maintenance_code','item_ids','vehicle_detail')

        extra_kwargs = {'modified_at': {'read_only': True}, 'created_at': {'read_only': True},
                        'modified_by': {'read_only': True},'created_by': {'read_only': True},
                        'maintenance_code':{'read_only':True},'maintenance_type':{'read_only':True},

                       }



    def validate(self, attrs):
        return super().validate(attrs)


    def create(self, validated_data):
        request = self.context.get('request')
        vehicleid = validated_data.pop('vehicle_id')
        types=validated_data.pop('item_ids')
        user=request.user

        maintenance=Maintenance.objects.create(maintenance_code=generate_activation_code("M"),vehicle_id=vehicleid,
                                               modified_by=user,
                                               created_by=user,created_at=now(),modified_at=now(),**validated_data )

        maintenance.maintenance_type.add(*types)

        approve=create_invoice(purpose=maintenance.maintenance_code,total=maintenance.maintenance_cost,
                               user=user, description= f"{vehicleid.custom_naming} Repairs")

        maintenance.invoice_id=approve
        maintenance.save()
        return maintenance

    def update(self, instance, validated_data):
        request = self.context.get('request')
        user=request.user
        instance.maintenance_cost = validated_data.get('maintenance_cost', instance.maintenance_cost)
        instance.maintenance_date= validated_data.get('maintenance_date', instance.maintenance_date)
        instance.due_date = validated_data.get('due_date', instance.due_date)
        instance.modified_by=user
        instance.modified_at=now()
        instance.maintenance_type.clear()
        for i in request.data["item_ids"]:
            instance.maintenance_type.add(i)
        instance.save()
        return instance

class VehicleRepairSerializer(serializers.ModelSerializer):
    created_by = UserDetailSerializer(read_only=True)
    modified_by = UserDetailSerializer(read_only=True)
    vehicle_detail = VehicleDetailSerializer(read_only=True,source='vehicle_d')
    class Meta:
        model = VehicleRepair
        fields =('id',  'modified_at', 'created_at', 'modified_by', 'created_by', 'vehicle_id', 'repair_date',
                 'repair_descriptions', 'repair_cost', 'repair_code','vehicle_detail')

        extra_kwargs = {'modified_at': {'read_only': True}, 'created_at': {'read_only': True},
                        'modified_by': {'read_only': True},'created_by': {'read_only': True},
                        'repair_code': {'read_only': True},
                        }

    def validate(self, attrs):
        return super().validate(attrs)


    def create(self, validated_data):
        request = self.context.get('request')
        vehicleid = validated_data.pop('vehicle_id')
        user=request.user

        repair=VehicleRepair.objects.create(repair_code=generate_activation_code("R"),vehicle_id=vehicleid,
                                               modified_by=user,
                                               created_by=user,created_at=now(),modified_at=now(),**validated_data )


        approve=create_invoice(purpose=repair.repair_code ,total=repair.repair_cost,user=user,
                               description=f"{vehicleid.custom_naming} Repairs")

        repair.invoice_id=approve
        repair.save()
        return repair

    def update(self, instance, validated_data):
        request = self.context.get('request')
        user=request.user
        instance.repair_cost = validated_data.get('repair_cost', instance.repair_cost)
        instance.repair_descriptions = validated_data.get('repair_descriptions', instance.repair_descriptions)
        instance.repair_date= validated_data.get('repair_date', instance.repair_date)
        instance.modified_by=user
        instance.modified_at=now()
        instance.save()
        return instance

class VehicleSerializer(serializers.ModelSerializer):
    created_by = UserDetailSerializer(read_only=True)
    modified_by = UserDetailSerializer(read_only=True)
    #vehicle_maintenance = MaintenanceSerializer(required=False, source='maintaince_history', many=True, read_only=True)
    #vehicle_repair = VehicleRepairSerializer(required=False, source='repair_history', many=True, read_only=True)

    class Meta:
        model = Vehicle
        fields =('id',  'modified_at', 'created_at', 'modified_by', 'created_by', 'vehicle_make', 'vehicle_model',
                 'vin', 'reg_number', 'vehicle_type', 'color','sitting_capacity','custom_naming','vehicle_condition',
                 'is_available')
        extra_kwargs = {'modified_at': {'read_only': True}, 'created_at': {'read_only': True},
                        'modified_by': {'read_only': True},'created_by': {'read_only': True},
                        'is_available': {'read_only': True}
                        }

    def validate(self, attrs):
        return super().validate(attrs)


    def create(self, validated_data):
        request = self.context.get('request')
        user=request.user
        return Vehicle.objects.create(modified_by=user,created_by=user,created_at=now(),modified_at=now(),**validated_data )



    def update(self, instance, validated_data):
        request = self.context.get('request')
        user=request.user

        instance.vin = validated_data.get('vin', instance.vin)
        instance.reg_number = validated_data.get('reg_number', instance.reg_number)
        instance.vehicle_type = validated_data.get('vehicle_type', instance.vehicle_type)
        instance.color = validated_data.get('color', instance.color)
        instance.sitting_capacity = validated_data.get('sitting_capacity', instance.sitting_capacity)
        instance.custom_naming = validated_data.get('custom_naming', instance.custom_naming)
        instance.vehicle_condition = validated_data.get('vehicle_condition', instance.vehicle_condition)

        instance.modified_by=user
        instance.modified_at=now()
        instance.save()
        return instance

class DriverSerializer(serializers.ModelSerializer):
    created_by = UserDetailSerializer(read_only=True)
    modified_by = UserDetailSerializer(read_only=True)
    class Meta:
        model = Driver
        fields =('id',  'modified_at', 'created_at','image', 'modified_by', 'created_by', 'first_name', 'address',
                 'last_name', 'phone', 'address', 'driver_license','nk_full_name','nk_contact',
                 'relationship','nk_address','expiry_date', 'number_trips','is_license_active','driver_number')

        extra_kwargs = {'modified_at': {'read_only': True}, 'created_at': {'read_only': True},
                        'modified_by': {'read_only': True},'created_by': {'read_only': True},
                        'is_license_active': {'read_only': True},
                        'number_trips': {'read_only': True}, 'driver_number': {'read_only': True},
                        'image': {'read_only': True}  }

    def create(self, validated_data):
        request = self.context.get('request')
        user=request.user
        return Driver.objects.create(driver_number=generate_activation_code("G"),modified_by=user,
                                        created_by=user,created_at=now(),modified_at=now(),**validated_data )


    def update(self, instance, validated_data):
        request = self.context.get('request')
        user=request.user

        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.address = validated_data.get('address', instance.address)
        instance.phone = validated_data.get('phone', instance.phone)
        instance.driver_license = validated_data.get('driver_license', instance.driver_license)
        instance.nk_full_name = validated_data.get('nk_full_name', instance.nk_full_name )
        instance.nk_contact = validated_data.get('nk_contact', instance.nk_contact )
        instance.relationship = validated_data.get('relationship', instance.relationship)
        instance.nk_address = validated_data.get('nk_address', instance.nk_address)
        instance.modified_by=user
        instance.modified_at=now()
        instance.save()
        return instance




