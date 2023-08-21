from django.conf import settings
from django.db import models
from .choices import OperatorStatus



class Operator(models.Model):
    """
    Profile model for the user - operator
    """
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='operator', default=None)
    status=models.CharField(default=OperatorStatus.OFFLINE,choices=OperatorStatus.choices,max_length=50,null=True,blank=True)
    robot_id=models.OneToOneField("robot.BasicInfo",on_delete=models.CASCADE,null=True,blank=True)


    def email(self):
        return self.user.email

    def first_name(self):
        return self.user.first_name

    def last_name(self):
        return self.user.last_name

    def role(self):
        return self.user.role
    
    def __str__(self):
        return str(self.user)