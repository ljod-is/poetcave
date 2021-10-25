from django import template
from django.conf import settings
from django.utils.safestring import mark_safe
from poem.models import Author

register = template.Library()

@register.simple_tag()
def private_paths():
    links = ''

    authors = Author.objects.exclude(private_path=None)
    for author in authors:
        links += '<a href="%s" class="einkaslod">%s/%s</a><br />\n' % (
            author.get_absolute_url(),
            settings.INSTANCE_FANCY_URL,
            author.private_path
        )

    return mark_safe(links)
