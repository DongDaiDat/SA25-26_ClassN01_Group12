import uuid

from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework import status


class ApiRenderer(JSONRenderer):
    def render(self, data, accepted_media_type=None, renderer_context=None):
        response = renderer_context.get("response") if renderer_context else None
        request = renderer_context.get("request") if renderer_context else None
        trace_id = getattr(request, "request_id", None)

        if response is None:
            return super().render(data, accepted_media_type, renderer_context)

        # If already in our envelope, pass through
        if isinstance(data, dict) and ("data" in data or "error" in data):
            return super().render(data, accepted_media_type, renderer_context)

        if response.status_code >= 400:
            # DRF may call renderer on errors too; ensure envelope
            err = {
                "error": {
                    "code": getattr(response, "error_code", "ERROR"),
                    "message": getattr(response, "error_message", "Request failed"),
                    "details": data,
                    "trace_id": trace_id,
                }
            }
            return super().render(err, accepted_media_type, renderer_context)

        envelope = {"data": data, "meta": {"trace_id": trace_id}}
        return super().render(envelope, accepted_media_type, renderer_context)


def exception_handler(exc, context):
    """
    Custom DRF exception handler.

    IMPORTANT: Lazy import DRF's default exception_handler to avoid circular import:
    settings -> DEFAULT_RENDERER_CLASSES -> modules.shared.api.ApiRenderer -> (this module)
    """
    # Lazy import to avoid circular import at Django startup
    from rest_framework.views import exception_handler as drf_exception_handler

    request = context.get("request")
    trace_id = getattr(request, "request_id", None)

    resp = drf_exception_handler(exc, context)

    if resp is None:
        # unhandled
        return Response(
            {
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "Internal server error",
                    "details": str(exc),
                    "trace_id": trace_id,
                }
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    code = getattr(exc, "code", None) or getattr(resp, "default_code", None) or "ERROR"
    message = getattr(exc, "detail", None)
    if isinstance(message, (dict, list)):
        msg_text = "Validation error"
    else:
        msg_text = str(message) if message else "Request failed"

    resp.data = {
        "error": {
            "code": str(code).upper(),
            "message": msg_text,
            "details": resp.data,
            "trace_id": trace_id,
        }
    }
    return resp


def new_request_id():
    return str(uuid.uuid4())
