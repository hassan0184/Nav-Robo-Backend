from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework import status
from operators.api.serializers import OperatorSerializer
from operators.models import Operator
from robot.models import BasicInfo
from rest_framework.exceptions import ValidationError
from firebase_client import client, robot_firebase
from operators.choices import OperatorStatus
from Trips.models import Trip
from Trips.choices import RideStatus
import roslibpy
from datetime import datetime
from firebase_admin import firestore
from pyfcm import FCMNotification



class OperatorViewSet(ModelViewSet):
    queryset = Operator.objects.all()
    serializer_class = OperatorSerializer

    @action(detail=False, methods=['GET', 'PATCH'], permission_classes=[IsAuthenticated])
    def me(self, request):
        if request.method == 'GET':
            (operator, created) = Operator.objects.get_or_create(user_id=request.user.id)
            serializer = OperatorSerializer(operator)
            return Response(serializer.data)

        elif request.method == 'PATCH':
            connected_status = request.query_params.get('status')
            operator_status = request.query_params.get('operator_status')
            operator = request.user.operator
            operator_obj = Operator.objects.filter(id=operator.id)
            if connected_status == "disconnect":
                robot_id = operator_obj.first()
                if robot_id.robot_id:
                    operator_obj.update(robot_id=None,status=OperatorStatus.OFFLINE)
                    robot_firebase.delete_by_id(robot_id.robot_id.robot_id)
                    return Response({"Success message": "robot is disconnected"}, status=status.HTTP_200_OK)
                    
                else:   
                    raise ValueError("No Robot Currently Connected")
                     
                    

            elif operator_status == "online":
                operator_obj.update(status=OperatorStatus.ONLINE)
                return Response({"Success message": "Operator status changed"}, status=status.HTTP_200_OK)

            elif operator_status == "offline":
                operator_obj.update(status=OperatorStatus.OFFLINE)
                return Response({"Success message": "Operator status changed"}, status=status.HTTP_200_OK)
            else:
                try:
                    robot_id = request.data.get('robot_id')
                    try:
                        robot_obj = client.get_by_id(robot_id)
                    except Exception as e:
                            raise ValueError("Incorrect Robot-Id")

                    if robot_obj.get('status') == "online":
                        robot, created = BasicInfo.objects.get_or_create(robot_id=robot_id)
                        if operator_obj.first().robot_id:
                            raise ValueError("Operator already connected with Robot {}".format(operator_obj.first().robot_id.robot_id))
                        else:        
                            try:
                                operator_obj.update(robot_id=robot)
                            except Exception as e:
                                raise ValueError("Robot is already connected with another Operator")

                            robot_firebase.create({"robot_id": robot_id})
                            return Response(status=status.HTTP_200_OK)
                    else:
                        raise ValueError("robot status is offline")
                except Exception as e:
                    raise ValidationError(e)

    @action(detail=False, methods=['PATCH'], permission_classes=[IsAuthenticated])
    def operator_response(self, request):
        try:
            trip_id = request.data.get('trip_id')
            ride_status = request.data.get('ride_status')
            robot_id = request.data.get('robot_id')
            device_token = request.data.get('device_token')
            trip_obj = Trip.objects.filter(trip_id=trip_id).first()
            if trip_obj:

                if ride_status == RideStatus.ACCEPTED.value:
                    trip_obj.status = RideStatus.ACCEPTED
                    update_data = {'status': 'accepted'}
                    robot_firebase.update(robot_id,update_data)
                    client.update(robot_id,{'is_available':False})
                    push_service = FCMNotification(api_key="AAAAX9Y56io:APA91bEikY12Tmt1ERgpuQS6UMm_M3qgcOai2KtFKdMth2z8T0zIlnKT_NgyoYAduZnzAbTeEhpS0GP86xV6SEdwgKvs8tVm15WDy3qZvI-E3m91innUBuPGz0a2qO0Bf4YTGOrmlyvS")
                    message_title = "Get Ready "
                    message_body = "Robot is on the way and will arrive in 5 minutes."
                    result = push_service.notify_single_device(registration_id=device_token, message_title=message_title, message_body=message_body)
                    trip_obj.save()
                    return Response(f"Trip status is now {trip_obj.status}", status=status.HTTP_200_OK)
                elif ride_status == RideStatus.CANCELED.value:
                    trip_obj.status = RideStatus.CANCELED
                    update_data = {'status': 'canceled'}
                    robot_firebase.update(robot_id, update_data)
                    client.update(robot_id, {'rider_list': firestore.ArrayUnion([int(trip_obj.rider.id)])})
                    trip_obj.save()
                    return Response(f"Trip status is now {trip_obj.status}", status=status.HTTP_200_OK)
                else:
                    raise ValueError("Invalid ride status provided")
            else:
                raise ValueError("Trip does not exist")

        except Exception as e:
            raise ValidationError(e)

    @action(detail=False, methods=['POST'], permission_classes=[IsAuthenticated])
    def setRobotCommands(self, request):
        try:
            # motor_status = request.query_params.get('status')
            # robot_node=client.get_by_id(request.user.operator.robot_id.robot_id)
            # connection_url=robot_node.get('url')
            # ros = roslibpy.Ros(connection_url, port=9090)
            # ros.run()
            # if ros.is_connected:
            #     enable_robot_client = roslibpy.Service(ros, '/enable_robot', 'std_:srvs/SetBool')
            #     if motor_status == 'on':
            #         request_data={'data': True}
            #     else:
            #         request_data={'data': False}
            #         update_data = {'status': 'arrived'}
            #         robot_firebase.update(request.user.operator.robot_id.robot_id,update_data)
            #     request = roslibpy.ServiceRequest(request_data)
            #     enable_robot_client.call(request)
                # return Response({'message': 'Robot command executed'}, status=status.HTTP_200_OK)
            motor_status = request.query_params.get('status')
            if motor_status == 'off':
                update_data = {'status': 'arrived'}
                time_str = datetime.now().strftime('%H:%M:%S.%f')
                robot_firebase.update(request.user.operator.robot_id.robot_id,update_data)
                robot_firebase.update(request.user.operator.robot_id.robot_id,{ 'arrived_at':time_str})    
                device_token=robot_firebase.get_by_id(request.user.operator.robot_id.robot_id)
                push_service = FCMNotification(api_key="AAAAX9Y56io:APA91bEikY12Tmt1ERgpuQS6UMm_M3qgcOai2KtFKdMth2z8T0zIlnKT_NgyoYAduZnzAbTeEhpS0GP86xV6SEdwgKvs8tVm15WDy3qZvI-E3m91innUBuPGz0a2qO0Bf4YTGOrmlyvS")
                message_title = "Robot is Arrived "
                message_body = "Your robot has arrived and is waiting for you at your pick up address."
                result = push_service.notify_single_device(registration_id=device_token.get('device_token'), message_title=message_title, message_body=message_body)
            return Response({'message': 'Robot command executed'}, status=status.HTTP_200_OK)
        except Exception as e:
            raise ValidationError(e)

        


            
    @action(detail=False, methods=['PATCH'], permission_classes=[IsAuthenticated])
    def tripend(self,request):
        try:
            robot_id = self.request.user.operator.robot_id.robot_id
            robot_firebase.delete_all_fields_by_id(robot_id)
            client.update(robot_id,{'is_available':True})
        
        except Exception as e:
            raise ValidationError(e)
        return Response({ 'message': 'Ride Ended'}, status=status.HTTP_200_OK)

