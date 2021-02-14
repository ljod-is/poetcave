from django.conf import settings
from django.db import models
from django.utils.translation import ugettext as _


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
        if self.year_born is not None:
            return '%s (%d)' % (self.name, self.year_born)
        else:
            return self.name


class Poem(models.Model):
    objects = PoemManager()

    EDITORIAL_STATUS_CHOICES = (
        ('pending', _('Pending')),
        ('approved', _('Approved')),
        ('rejected', _('Rejected')),
    )

    author = models.ForeignKey('poem.Author', related_name='poems', on_delete=models.CASCADE)

    name = models.CharField(max_length=50, null=False, blank=False)
    body = models.TextField(null=False, blank=False)
    about = models.TextField(null=True, blank=True)

    # Wishes of the user.
    public = models.BooleanField(default=False)
    public_timing = models.DateTimeField(null=True, blank=True)

    editorial_status = models.CharField(max_length=20, choices=EDITORIAL_STATUS_CHOICES, default='pending')
    editorial_user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL)
    editorial_timing = models.DateTimeField(null=True, blank=True)
    editorial_reason = models.TextField(null=True, blank=True)

    def __str__(self):
        return '%s - %s' % (self.name, self.author)
