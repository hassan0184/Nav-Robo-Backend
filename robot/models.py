from django.db import models


class BasicInfo(models.Model):
    robot_id = models.name = models.CharField(max_length=50)

    class Meta:
        verbose_name_plural = "Robot Information"

    def __str__(self):
        return str(self.robot_id)
