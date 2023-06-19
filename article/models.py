from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _


class ArticleQuerySet(models.QuerySet):
    # Limits articles to those that the given user has access to. Reporters
    # have access to them all, but others only have access to published ones.
    def visible_to(self, user):
        if user.is_authenticated and user.is_reporter:
            return self
        else:
            return self.filter(editorial_status='published')


class Article(models.Model):
    objects = ArticleQuerySet.as_manager()

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

    def get_absolute_url(self):
        return reverse('article', kwargs={'article_id': self.id})

    class Meta:
        # ID is used in ordering also because news articles on the old
        # website didn't actually have timing.
        ordering = ['-editorial_timing', '-id']
