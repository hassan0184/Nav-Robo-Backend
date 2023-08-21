from rest_framework.viewsets import ModelViewSet
from rest_framework.exceptions import ValidationError
from rest_framework.generics import ListAPIView, CreateAPIView, RetrieveUpdateDestroyAPIView
from .serializers import TripSerializer
from Trips.models import Trip
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from Trips.choices import RideStatus
from firebase_client import robot_firebase
from firebase_client import client
from datetime import datetime,timedelta
import googlemaps
import os
import re
import roslibpy
from pyfcm import FCMNotification
from threading import Thread


class TripRelatedView(ModelViewSet):
    serializer_class = TripSerializer

    def get_object(self):
        try:
            queryset = Trip.objects.get(rider=self.request.user.rider, trip_id=self.kwargs.get('pk'))
            return queryset
        except Exception as e:
            raise ValidationError(e)

    @action(detail=False, methods=['GET'], permission_classes=[IsAuthenticated])
    def history(self, request):
        try:
            serializer = TripSerializer(
                Trip.objects.filter(rider=self.request.user.rider, status=RideStatus.COMPLETED).order_by('-id'),
                many=True)
            return Response(serializer.data)
        except Exception as e:
            raise ValidationError(e)

    def destroy(self, request, *args, **kwargs):
        response = self.perform_destroy()
        return response

    def perform_destroy(self):
        if self.request.query_params.get("notify") == 'True':
            trips_set=robot_firebase.all()
            try:
                for trip in trips_set:
                    id=Trip.objects.filter(trip_id=trip.get('trip_id')).first()
                    instance=id
                    now=datetime.now()
                    arrived_at_str=trip.get('arrived_at')
                    arrived_at_time = datetime.strptime(arrived_at_str, '%H:%M:%S.%f').time()
                    now_datetime = datetime.combine(datetime.today(), now.time())
                    arrived_at_datetime = datetime.combine(datetime.today(), arrived_at_time)
                    time_diff = now_datetime - arrived_at_datetime
                    if time_diff > timedelta(minutes=5):
                        device_token = trip.get('device_token')
                        return instance.delete(push_service=FCMNotification(
                            api_key="AAAAX9Y56io:APA91bEikY12Tmt1ERgpuQS6UMm_M3qgcOai2KtFKdMth2z8T0zIlnKT_NgyoYAduZnzAbTeEhpS0GP86xV6SEdwgKvs8tVm15WDy3qZvI-E3m91innUBuPGz0a2qO0Bf4YTGOrmlyvS"),
                                            registration_id=device_token,
                                            message_title="Ride is Cancelled ",
                                            message_body="You were not at your pick up address, so your robot ride was canceled.")
            except Exception as e:
                raise ValidationError(e)

        else:
            instance = self.get_object()
            return instance.delete()

    @action(detail=True, methods=['PATCH'], permission_classes=[IsAuthenticated])
    def feedback(self, request, pk=None):
        try:
            queryset = self.get_object()  # Retrieve the object with the pk from the URL parameter
            queryset.comment = self.request.data.get('comment')
            queryset.trip_feedback = self.request.data.get('emoji')
            queryset.save()
            return Response({"Success message": "Trip object is updated"}, status=status.HTTP_200_OK)
        except Exception as e:
            raise ValidationError(e)

    @action(detail=True, methods=['PATCH'], permission_classes=[IsAuthenticated])
    def startride(self, request, pk=None):
        try:
            queryset = self.get_object()  # Retrieve the object with the pk from the URL parameter
            queryset.status = RideStatus.STARTED
            update_data = {'status': 'started'}
            robot_firebase.update(queryset.robot.robot_id, update_data)
            queryset.save()
            return Response({"Success message": "Trip object is Started"}, status=status.HTTP_200_OK)
        except Exception as e:
            raise ValidationError(e)

    @action(detail=True, methods=['PATCH'], permission_classes=[IsAuthenticated])
    def unlockrobot(self, request, pk=None):
        try:
            queryset = self.get_object()  # Retrieve the object with the pk from the URL parameter
            rider_latitude = self.request.data.get('rider_latitude')
            rider_longitude = self.request.data.get('rider_longitude')
            robot = client.get_by_id(queryset.robot.robot_id)
            now = datetime.now()
            g_maps = googlemaps.Client(key=os.environ['GOOGLE_MAPS_SECRET_KEY'])
            source = (rider_latitude, rider_longitude)
            destination = (robot.get('position').latitude, robot.get('position').longitude)
            direction_result = g_maps.directions(source, destination, mode="walking", departure_time=now)
            distance_ft = int(re.findall('\d+', direction_result[0]['legs'][0].get('distance')['text'])[0])
            if distance_ft <= 50:
                # ros = roslibpy.Ros('magicbycalvin.duckdns.org', port=9090)
                # ros.run()
                # if ros.is_connected:
                #     enable_robot_client = roslibpy.Service(ros, '/enable_robot', 'std_srvs/SetBool')
                #     request_data = {'data': True}
                #     request = roslibpy.ServiceRequest(request_data)
                #     enable_robot_client.call(request)
                return Response({"Success message": "Robot is unlocked"}, status=status.HTTP_200_OK)
            else:
                raise ValueError("Move closer to robot and try again")
        except Exception as e:
            raise ValidationError(e)

    @action(detail=False, methods=['GET'], permission_classes=[])
    def closest_robot(self, request):
        try:
            t = Thread(target=TripRelatedView.closest_robot_thread)
            t.start()
            return Response("Robot search started in background", status=status.HTTP_200_OK)
        except Exception as e:
            raise ValidationError(e)

    def closest_robot_thread():
        try:
            device_token = []
            stored_data = robot_firebase.filter('status', '==', 'accepted')
            for data in stored_data:
                robot = client.get_by_id(data.get('id').strip())
                now = datetime.now()
                g_maps = googlemaps.Client(key=os.environ['GOOGLE_MAPS_SECRET_KEY'])
                source = (robot.get('position').latitude, robot.get('position').longitude)
                destination = (data.get('position').latitude, data.get('position').longitude)
                direction_result = g_maps.directions((robot.get('position').latitude, robot.get('position').longitude),
                                                     (data.get('position').latitude, data.get('position').longitude),
                                                     mode="driving", departure_time=now)
                duration_value = direction_result[0]['legs'][0]['duration']['value']
                # if 10 <= duration_value <= 60:
                #     device_token.append(data.get('device_token'))
                # else:
                #     continue
                device_token.append(data.get('device_token'))
            if device_token:
                push_service = FCMNotification(
                    api_key="AAAAX9Y56io:APA91bEikY12Tmt1ERgpuQS6UMm_M3qgcOai2KtFKdMth2z8T0zIlnKT_NgyoYAduZnzAbTeEhpS0GP86xV6SEdwgKvs8tVm15WDy3qZvI-E3m91innUBuPGz0a2qO0Bf4YTGOrmlyvS")
                message_title = "Robot is 1 minute away "
                message_body = "Your robot is 1 minute away and will arrive soon."
                result = push_service.notify_multiple_devices(registration_ids=device_token,
                                                              message_title=message_title, message_body=message_body)
                return Response(f"Robot is 1 minute away ", status=status.HTTP_200_OK)
            else:
                raise ValueError("No closest robot")
        except Exception as e:
            raise ValidationError(e)
