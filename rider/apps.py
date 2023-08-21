from django.apps import AppConfig


class RiderConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'rider'
    def ready(self):
        import rider.signals