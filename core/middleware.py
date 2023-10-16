from django.conf import settings
from django.http import JsonResponse


def api_exception_middleware(get_response):
    def middleware(request):
        response = get_response(request)

        m = request.resolver_match  # Short-hand.
        is_ninja = m is not None and "ninja" in m.app_names

        if not is_ninja or response.status_code == 200:
            return response
        else:
            return JsonResponse(
                {
                    "error": {
                        "code": response.status_code,
                        "trace": str(response.content) if settings.DEBUG else "",
                    }
                },
                status=response.status_code,
            )

    return middleware
