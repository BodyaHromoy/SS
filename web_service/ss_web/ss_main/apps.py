from django.apps import AppConfig


class SsMainConfig(AppConfig):
    name = 'ss_main'

    def ready(self):
        import ss_main.signals
