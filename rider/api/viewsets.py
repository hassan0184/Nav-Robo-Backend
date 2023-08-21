from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from firebase_client import client
from rider.api.serializers import RiderSerializer
from rider.models import Rider
from rest_framework import status



class RiderViewSet(ModelViewSet):
    queryset = Rider.objects.all()
    serializer_class = RiderSerializer

    @action(detail=False, methods=['GET', 'PATCH'], permission_classes=[IsAuthenticated])
    def me(self, request):
        (rider, created) = Rider.objects.get_or_create(user_id=request.user.id)
        if request.method == 'GET':
            serializer = RiderSerializer(rider)
            return Response(serializer.data)

        elif request.method == 'PATCH':
            serializer = RiderSerializer(rider, data=request.data, context={'request': request})
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)

    @action(detail=False, methods=['PATCH'], permission_classes=[IsAuthenticated])
    def remove_rider(self, request):
        '''remove rider from the list of riders in firebase node'''
        
        client.remove_value_from_array_in_all_docs('rider_list',self.request.user.rider.id)
        return Response({"Success message":"Rider is Removed From all documents"}, status=status.HTTP_200_OK)