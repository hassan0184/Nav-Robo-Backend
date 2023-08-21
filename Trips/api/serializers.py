import googlemaps
import os
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from django.http import JsonResponse
from firebase_client import robot_firebase
from ..models import Trip, Fare
from ..choices import RideStatus
from firebase_client import client
from Trips.utils import closest_robot
from robot.models import BasicInfo
from operators.models import Operator
from operators.choices import OperatorStatus
from datetime import datetime


class TripSerializer(serializers.ModelSerializer):
    robot = serializers.SerializerMethodField(read_only=True)

    def get_robot(self, obj):
        try:
            data = BasicInfo.objects.filter(robot_id=obj.robot.robot_id).first()
            return data.robot_id
        except Exception as e:
            raise ValidationError(e)

    class Meta:
        model = Trip
        fields = ['trip_id', 'estimating_time', 'estimating_distance', 'pickup_location', 'pickup_lat', 'pickup_lng',
                  'pickup_datetime', 'dropoff_location', 'dropoff_datetime', 'distance_traveled', 'status', 'cost',
                  'rider', 'robot', 'ride_time']

    def create(self, validated_data):
        try:
            validated_data["rider"] = self.context["request"].user.rider
            if validated_data["rider"].is_pending_payment == False:
                current_latitude = self.context["request"].data.get('pickup_lat')
                current_longitude = self.context["request"].data.get('pickup_lng')
                closest_location = None
                closest_distance = float('inf')
                stored_data = client.filter('status', '==', 'online')
                online_robot_ids = Operator.objects.filter(status=OperatorStatus.ONLINE).values_list(
                    'robot_id__robot_id', flat=True)
                stored_data = [data for data in stored_data if data.get('id') in online_robot_ids]

                for i in stored_data:
                    if "is_available" in i.keys():
                        closest_location, closest_distance = closest_robot(validated_data["rider"].id, i,
                                                                           current_latitude, current_longitude,
                                                                           closest_location, closest_distance)
                    else:
                        client.update(i.get('id'), {'is_available': True})
                        closest_location, closest_distance = closest_robot(validated_data["rider"].id, i,
                                                                           current_latitude, current_longitude,
                                                                           closest_location, closest_distance)

                if closest_location:
                    operator_obj = Operator.objects.filter(robot_id__robot_id=closest_location.get('id'),
                                                           status=OperatorStatus.ONLINE).first()
                    if operator_obj:
                        now = datetime.now()
                        g_maps = googlemaps.Client(key=os.environ['GOOGLE_MAPS_SECRET_KEY'])

                        source = (closest_location.get('position').latitude, closest_location.get('position').longitude)
                        destination = (current_latitude, current_longitude)
                        direction_result = g_maps.directions(
                            (closest_location.get('position').latitude, closest_location.get('position').longitude),
                            (current_latitude, current_longitude), mode="driving", departure_time=now)

                        if direction_result[0]['legs'][0]['distance']['value'] * 0.000621371 <= 5:
                            validated_data["estimating_time"] = direction_result[0]['legs'][0]['duration']['text']
                            validated_data["estimating_distance"] = direction_result[0]['legs'][0]['distance']['text']
                            validated_data["robot"], created = BasicInfo.objects.get_or_create(
                                robot_id=closest_location.get('id'))
                            return super().create(validated_data)
                        else:
                            raise ValueError("No robot currently available in your area")
                    else:
                        raise ValueError("No robot currently available in your area")

                else:

                    client.remove_value_from_array_in_all_docs('rider_list', validated_data['rider'].id)
                    raise ValueError("No robot Available RightNow")
            else:
                raise ValueError("You cannot Create New Trip due to Pending Payment.")




        except Exception as e:
            raise ValidationError(e)

    def update(self, instance, validated_data):
        try:
            instance.dropoff_location = validated_data['dropoff_location']
            instance.dropoff_datetime = validated_data['dropoff_datetime']
            instance.distance_traveled = validated_data['distance_traveled']
            instance.ride_time = validated_data['ride_time']
            instance.status = RideStatus.COMPLETED
            fare_object = Fare.objects.all().values("cost_per_mi").first()
            instance.cost = validated_data['distance_traveled'] * fare_object.get('cost_per_mi')
            instance.cost = instance.cost * 100
            # Add flat fee in cents
            instance.cost = instance.cost + int(os.environ['FLAT_FEE'])
            instance.save()
            robot_obj = BasicInfo.objects.filter(id=instance.robot_id).first()
            update_data = {'status': 'completed'}
            robot_firebase.update(robot_obj.robot_id, update_data)
            client.remove_value_from_array_in_all_docs('rider_list', instance.rider.id)
            return instance
        except Exception as e:
            raise ValidationError(e)
