from rest_framework import serializers

class ExampleSerializer(serializers.Serializer):
    example_field = serializers.CharField()
