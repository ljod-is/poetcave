from datetime import timedelta
from django import template
from django.template.defaultfilters import date
from django.utils import timezone
from poem.models import DayPoem

register = template.Library()

@register.filter()
def is_today(dt):
    return dt is not None and dt == timezone.now().date()
