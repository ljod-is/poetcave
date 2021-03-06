from django.conf import settings

def globals(request):
    return {
        'letters': settings.ALPHABET[settings.LANGUAGE_CODE]['letters'],
        'NEWEST_COUNT': settings.NEWEST_COUNT,
    }
