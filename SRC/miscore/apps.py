from django.apps import AppConfig
class MiscoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'miscore'
class MiscoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "miscore"

    def ready(self):
        # nạp signal
        from . import signals  # noqa