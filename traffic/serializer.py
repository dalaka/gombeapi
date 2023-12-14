from django.utils.timezone import now
from rest_framework import serializers

from traffic.models import Route


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
