from rest_framework.exceptions import ValidationError
from rest_framework.generics import ListAPIView,CreateAPIView,RetrieveUpdateDestroyAPIView
from .api.serializers import TripSerializer
from .models import Trip


class TripRelatedView(CreateAPIView,RetrieveUpdateDestroyAPIView):
    serializer_class = TripSerializer

    def get_object(self):
        try:
            queryset=Trip.objects.get(rider=self.request.user.rider,trip_id=self.kwargs.get('pk'))
            return queryset
        except Exception as e:
            raise ValidationError(e)

class TransactionHistoryView(ListAPIView):
    serializer_class = TripSerializer
    def get_queryset(self):
        return Trip.objects.filter(rider=self.request.user.rider)
  
        

