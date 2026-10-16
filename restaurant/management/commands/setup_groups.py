from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group

class Command(BaseCommand):
    help = "Create the Manager and Delivery crew groups."

    def handle(self, *args, **options):
        for name in ("Manager", "Delivery crew"):
            Group.objects.get_or_create(name=name)
            self.stdout.write(self.style.SUCCESS(f"Group ready: {name}"))
