from rest_framework import serializers
from target.models import Target_Master,Target_Details


class Target_Master_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Target_Master
        fields = '__all__'

class Target_Details_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Target_Details
        fields = '__all__'

