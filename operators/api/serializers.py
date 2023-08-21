from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from operators.models import Operator
from robot.models import BasicInfo
from Trips.models import Trip
from Trips.choices import RideStatus



class OperatorSerializer(serializers.ModelSerializer):
    robot = serializers.SerializerMethodField(read_only=True)
    def get_robot(self, obj):
        if obj.robot_id:
            data = BasicInfo.objects.filter(robot_id= obj.robot_id.robot_id).first()
            return data.robot_id
        else:
            return None
    class Meta:
        model = Operator
        fields = ['user_id', 'email','status', 'role', 'first_name', 'last_name','robot']
    