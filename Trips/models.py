from django.db import models
from .choices import RideStatus,TripFeedback
from random import randint
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from django.utils.translation import gettext_lazy as _
from firebase_client import  robot_firebase,client



class Trip(models.Model):
    trip_id = models.IntegerField(blank=True, null=True)
    estimating_time = models.CharField(max_length=255, blank=True, null=True)
    pickup_location = models.CharField(max_length=255)
    pickup_lat = models.DecimalField(_('Latitude'), max_digits=20, decimal_places=8, default=None)
    pickup_lng = models.DecimalField(_('Longitude'), max_digits=20, decimal_places=8, default=None)
    pickup_datetime = models.DateTimeField()
    dropoff_location = models.CharField(max_length=255,null=True,blank=True)
    dropoff_datetime = models.DateTimeField(null=True,blank=True)
    distance_traveled = models.FloatField(null=True,blank=True)
    status=models.CharField(max_length=255,choices=RideStatus.choices,default=RideStatus.INITIATED)
    cost=models.FloatField(null=True,blank=True)
    rider=models.ForeignKey("rider.Rider",on_delete=models.PROTECT,null=True,blank=True)
    robot=models.ForeignKey("robot.BasicInfo",on_delete=models.PROTECT,null=True,blank=True)
    comment=models.TextField(blank=True,null=True)
    trip_feedback=models.CharField(max_length=200,choices=TripFeedback.choices,default=TripFeedback.LIKED)
    estimating_distance = models.CharField(max_length=255, blank=True, null=True)
    ride_time=models.CharField(blank=True,null=True,max_length=50)

    

    def __str__(self):
        return str(self.rider)

    def save(self, *args, **kwargs):
        if self.trip_id:
            super(Trip, self).save(*args, **kwargs)
        else:
            self.trip_id = randint(100, 999)
            super(Trip, self).save(*args, **kwargs)
    

    def delete(self, *args, **kwargs):
        try:
            if self.status == RideStatus.COMPLETED:
                response_data = {"status": "success",
                                 "message": "you cannot delete this ride.because,it is already completed!"}
                return Response(data=response_data)
            else:
                if kwargs.get('push_service') and kwargs.get('registration_id'):
                    push_service = kwargs.pop('push_service')
                    registration_id = kwargs.pop('registration_id')
                    message_title = kwargs.pop('message_title')
                    message_body = kwargs.pop('message_body')
                    result = push_service.notify_single_device(
                        registration_id=registration_id,
                        message_title=message_title,
                        message_body=message_body
                        )
                    self.status = RideStatus.CANCELED
                    robot_firebase.delete_all_fields_by_id(self.robot.robot_id)
                    client.remove_value_from_array_in_all_docs('rider_list',self.rider.id)
                    client.update(self.robot.robot_id,{'is_available':True})
                    super(Trip, self).save(*args, **kwargs)
                    response_data = {"status": "success", "message": "Your ride status is now Canceled!"}
                    return Response(data=response_data)
                else:
                    self.status = RideStatus.CANCELED
                    robot_firebase.delete_all_fields_by_id(self.robot.robot_id)
                    client.remove_value_from_array_in_all_docs('rider_list',self.rider.id)
                    client.update(self.robot.robot_id,{'is_available':True})
                    super(Trip, self).save(*args, **kwargs)
                    response_data = {"status": "success", "message": "Your ride status is now Canceled!"}
                    return Response(data=response_data)
        except Exception as e:
            raise ValidationError(e)


class Fare(models.Model):
    cost_per_mi = models.IntegerField()

    def __str__(self):
        return str(self.cost_per_mi)

    class Meta:
        verbose_name_plural = "Cost Per Miles"
