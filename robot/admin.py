from django.contrib import admin
from .models import BasicInfo


class RobotAdminView(admin.ModelAdmin):
    list_display = ['id', 'robot_id']


admin.site.register(BasicInfo, RobotAdminView)
