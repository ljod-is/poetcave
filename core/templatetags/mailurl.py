from django import template
from django.urls import reverse
from django_middleware_global_request.middleware import get_request

register = template.Library()


# A template tag to replace `url` for when we don't have access to the
# request inside the template.
@register.simple_tag()
def mailurl(view_name, *args):
    request = get_request()
    path = reverse(view_name, args=args)

    if request is not None:
        return request.build_absolute_uri(path)
    else:
        # TODO: This could theoretically be improved to check the settings or
        # the Site framework or whatever else to figure out what to place
        # before the path. Honestly, we can't be bothered at this point,
        # since we have no need for it. Feel free to improve.
        return path
