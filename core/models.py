from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    # Fields beginning with `contact_` are only intende for use by
    # administrators, not for displaying on the web.
    contact_name = models.CharField(max_length=100)
    contact_address = models.CharField(max_length=100, null=True, blank=True)
    contact_postal_code = models.CharField(max_length=3, null=True, blank=True)
    contact_place = models.CharField(max_length=100, null=True, blank=True)
    contact_phone = models.CharField(max_length=30, null=True, blank=True)

    # User's associated author. This separation is done because there may be
    # authors without associated users and possibly users without associated
    # authors. It is also possible that a user may administer many authors in
    # the future, or one author being managed by multiple users, such as
    # historical authors whose work has fallen out of copyright.
    #
    # However, the overwhelming majority of authors and users will have
    # exactly one of the other. For this reason, making this a
    # ManyToManyField will complicate both development and performance,
    # largely unnecessarily. If we want to create a ManyToManyField
    # relationship later, it will be a different field. The value in this
    # field means that the User and corresponding Author are the same person.
    author = models.OneToOneField('poem.Author', null=True, related_name='user', on_delete=models.SET_NULL)

    date_updated = models.DateTimeField(null=True, blank=True)
