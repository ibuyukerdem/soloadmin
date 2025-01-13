# common/base_serializer.py

from rest_framework import serializers


class BaseOnlyDateSerializer(serializers.ModelSerializer):
    date_format = "%d.%m.%Y"

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        for field_name in ['createdAt', 'updatedAt']:
            if field_name in representation and representation[field_name] is not None:
                field_value = getattr(instance, field_name)
                representation[field_name] = field_value.strftime(self.date_format)
        return representation


class BaseDateTimeSerializer(serializers.ModelSerializer):
    datetime_format = "%d.%m.%Y %H:%M"

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        for field_name in ['createdAt', 'updatedAt']:
            if field_name in representation and representation[field_name] is not None:
                field_value = getattr(instance, field_name)
                representation[field_name] = field_value.strftime(self.datetime_format)
        return representation
