import hmac

from django.conf import settings
from django.http import JsonResponse
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView

from services.deadlines import process_deadlines


def health(request):
    return JsonResponse({"status": "ok"})


class RunDeadlines(APIView):
    """Hourly job entrypoint (GitHub Actions). Idempotent. POST only, token protected (T9)."""
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        token = request.headers.get("X-Cron-Token", "")
        expected = settings.CRON_TOKEN
        if not expected or not hmac.compare_digest(token.encode(), expected.encode()):
            return JsonResponse({"detail": "unauthorized"}, status=401)
        return JsonResponse(process_deadlines())
