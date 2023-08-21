from django.contrib import admin

from operators.models import Operator


@admin.register(Operator)
class OperatorAdmin(admin.ModelAdmin):
    list_display = ["id","status","robot_id", "first_name", "last_name"]
    search_fields = ["id", "user__first_name", "user__last_name"]
    list_select_related = ['user']
