from django.conf import settings
from django.db import models


class AuthorManager(models.Manager):
    def managed_by(self, user):
        # NOTE: This will probably change in the future, if we implement
        # users' ability to control many authors. For now, we're assuming a
        # one-to-one relationship between the user and author. This function
        # currently exists to ease that transition, once it occurs.
        return self.filter(user=user)


class PoemManager(models.Manager):
    def managed_by(self, user):
        # NOTE: See note in `AuthorManager.managed_by`.
        return self.filter(author__user=user)


class Author(models.Model):
    objects = AuthorManager()

    name = models.CharField(max_length=100, null=False, blank=False)
    name_dative = models.CharField(max_length=100, null=False, blank=False)
    birth_year = models.SmallIntegerField(null=True, blank=True)
    death_year = models.SmallIntegerField(null=True, blank=True)
    about = models.TextField(null=True, blank=True)

    def __str__(self):
        return '%s (%d)' % (self.name, self.birth_year)


class Poem(models.Model):
    objects = PoemManager()

    author = models.ForeignKey('poem.Author', related_name='poems', on_delete=models.CASCADE)

    name = models.CharField(max_length=50, null=False, blank=False)
    body = models.TextField(null=False, blank=False)
    description = models.TextField(null=True, blank=True)

    # Whether the author wants the poem shown publicly or not.
    public = models.BooleanField(default=False)

    approved = models.BooleanField(default=False)
    approved_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL)
    approved_timing = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '%s - %s' % (self.name, self.author)
