from django.contrib import admin
from .models import Fare, Trip


class FareAdminView(admin.ModelAdmin):
    list_display = ['cost_per_mi']

    def has_add_permission(self, request):
        count = Fare.objects.all().count()
        if count == 0:
            return True
        return False


class TripAdminView(admin.ModelAdmin):
    list_display = ['rider', 'status', 'robot', 'pickup_location', 'estimating_time', 'ride_time']


admin.site.register(Trip, TripAdminView)
admin.site.register(Fare, FareAdminView)
