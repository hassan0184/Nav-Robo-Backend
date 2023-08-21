from django.core.management.base import BaseCommand
from users.models import User


class Command(BaseCommand):
    def handle(self, *args, **options):
        print("------------------------test---------------")
        if not User.objects.filter(email='admin@nav.com').exists():
            try:
                if not User.objects.filter(email="admin@nav.com").exists():
                    User.objects.create_superuser(
                        "admin@nav.com", "Password@123")
            except:
                pass
