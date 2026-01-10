import logging
import uuid

from django.utils.deprecation import MiddlewareMixin
from django.http import JsonResponse
from django.conf import settings
from django.contrib.auth.models import AnonymousUser

logger = logging.getLogger(__name__)


def _new_request_id() -> str:
    return str(uuid.uuid4())


class RequestIDMiddleware(MiddlewareMixin):
    """
    - Ensure every request has a request_id (from X-Request-Id or generated).
    - Ensure AnonymousUser has `.role` so schema generation (drf-spectacular) won't crash
      when some permission/view accesses request.user.role.
    """

    def process_request(self, request):
        # Request ID
        request_id = request.headers.get("X-Request-Id") or _new_request_id()
        request.request_id = request_id

        # ✅ Fix: make AnonymousUser safe for role-based code paths
        user = getattr(request, "user", None)
        if isinstance(user, AnonymousUser) and not hasattr(user, "role"):
            user.role = None

    def process_response(self, request, response):
        rid = getattr(request, "request_id", None)
        if rid:
            response["X-Request-Id"] = rid
        return response


class ApiExceptionMiddleware(MiddlewareMixin):
    """
    Catch unhandled exceptions and return a consistent JSON envelope.
    In DEBUG, you can allow Django's debug page by not swallowing exceptions
    (optional; controlled by settings.DEBUG).
    """

    def process_exception(self, request, exception):
        rid = getattr(request, "request_id", None)

        # Log stacktrace
        logger.exception("Unhandled exception", extra={"request_id": rid})

        # If you want Django debug page in dev, you can re-raise when DEBUG=True.
        # Comment these 2 lines if you always want JSON error.
        if getattr(settings, "DEBUG", False):
            return None

        return JsonResponse(
            {
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "Internal server error",
                    "details": str(exception),
                    "trace_id": rid,
                }
            },
            status=500,
        )
