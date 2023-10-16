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
            code = response.status_code
            trace = ""
            message = ""
            if code == 500:
                # 500 errors are special in that they are unexpected.
                if settings.DEBUG:
                    trace = response.content.decode("utf-8")
                    message = "See trace"
                else:
                    message = "Unknown error"
            else:
                # Other errors should explain themselves as messages.
                message = response.content.decode("utf-8")

            return JsonResponse(
                {
                    "error": {
                        "code": code,
                        "trace": trace,
                        "message": message,
                    }
                },
                status=response.status_code,
            )

    return middleware
