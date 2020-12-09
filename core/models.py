from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    name = models.CharField(max_length=100, null=False, blank=False)
    name_dative = models.CharField(max_length=100, null=False, blank=False)
    birth_year = models.SmallIntegerField(null=True, blank=True)

    about = models.TextField(null=True, blank=True)

    # Fields beginning with `contact_` are only intende for use by
    # administrators, not for displaying on the web.
    contact_name = models.CharField(max_length=100)
    contact_address = models.CharField(max_length=100, null=True, blank=True)
    contact_postal_code = models.CharField(max_length=3, null=True, blank=True)
    contact_place = models.CharField(max_length=100, null=True, blank=True)
    contact_phone = models.CharField(max_length=30, null=True, blank=True)
