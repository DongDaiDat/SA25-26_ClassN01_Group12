from django.apps import AppConfig


class SharedConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "modules.shared"

    def ready(self):
        """
        Make AnonymousUser safe for role-based checks.

        drf-spectacular may generate schema with AnonymousUser.
        Some permissions/views access request.user.role -> would crash.
        """
        from django.contrib.auth.models import AnonymousUser

        # Attach a default 'role' attribute so code like request.user.role won't crash
        if not hasattr(AnonymousUser, "role"):
            AnonymousUser.role = None
