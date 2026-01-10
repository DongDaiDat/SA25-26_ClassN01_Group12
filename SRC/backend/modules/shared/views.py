from django.http import JsonResponse

def health(request):
    return JsonResponse({"data": {"status": "ok"}, "meta": {"trace_id": getattr(request, "request_id", None)}}, status=200)
