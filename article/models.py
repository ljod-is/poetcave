from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _

class Article(models.Model):
    EDITORIAL_STATUS_CHOICES = [
        ('unpublished', _('Unpublished')),
        ('published', _('Published')),
    ]

    name = models.CharField(max_length=100)
    description = models.CharField(max_length=300)
    body = models.TextField()

    editorial_status = models.CharField(max_length=20, choices=EDITORIAL_STATUS_CHOICES, default='unpublished')
    editorial_user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL)
    editorial_timing = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        # ID is used in ordering also because news articles on the old
        # website didn't actually have timing.
        ordering = ['-editorial_timing', '-id']
