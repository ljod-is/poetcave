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
    year_born = models.SmallIntegerField(null=True, blank=True)
    year_dead = models.SmallIntegerField(null=True, blank=True)
    about = models.TextField(null=True, blank=True)

    # Author's associated user. This separation is done because there may be
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
    user = models.OneToOneField('core.User', null=True, related_name='author', on_delete=models.SET_NULL)

    # `date_joined` field for creation is provided by parent model.
    date_updated = models.DateTimeField(auto_now=True, null=True, blank=True)

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
