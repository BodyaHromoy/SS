from django.apps import AppConfig

class SsMainConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "ss_main"

    def ready(self):
        import ss_main.signals
