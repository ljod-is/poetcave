from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse

class User(AbstractUser):
    # Fields beginning with `contact_` are only intende for use by
    # administrators, not for displaying on the web.
    contact_name = models.CharField(max_length=100)
    contact_address = models.CharField(max_length=100, null=True, blank=True)
    contact_postal_code = models.CharField(max_length=3, null=True, blank=True)
    contact_place = models.CharField(max_length=100, null=True, blank=True)
    contact_phone = models.CharField(max_length=30, null=True, blank=True)

    # `date_joined` field for creation is provided by parent model.
    date_updated = models.DateTimeField(auto_now=True, null=True, blank=True)

    # Moderators approve or reject poems.
    is_moderator = models.BooleanField(default=False)

    def get_absolute_url(self):
        return reverse('user', args=(self.username,))
