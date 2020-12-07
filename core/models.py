from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    name = models.CharField(max_length=100)
    name_dative = models.CharField(max_length=100)
    birth_year = models.SmallIntegerField(null=True)

    about = models.TextField()

    # Fields beginning with `contact_` are only intende for use by
    # administrators, not for displaying on the web.
    contact_name = models.CharField(max_length=100)
    contact_address = models.CharField(max_length=100)
    contact_postal_code = models.CharField(max_length=3)
    contact_place = models.CharField(max_length=100)
    contact_phone = models.CharField(max_length=30)