from django.apps import AppConfig

class RestaurantConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "restaurant"

    def ready(self):
        from django.contrib.auth.models import Group
        # Groups are created by the setup_groups management command.
