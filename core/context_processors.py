from django.conf import settings

def globals(request):
    return {
        'letters': settings.ALPHABET[settings.LANGUAGE_CODE]['letters'],
        'INSTANCE_NAME': settings.INSTANCE_NAME,
        'INSTANCE_FANCY_URL': settings.INSTANCE_FANCY_URL,
        'NEWEST_COUNT': settings.NEWEST_COUNT,
        'CONTACT_EMAIL': settings.CONTACT_EMAIL,
        'MATOMO_URL': settings.MATOMO_URL,
    }
