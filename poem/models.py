from django.conf import settings
from django.db import models
from django.db.models import Prefetch
from django.db.models import Q
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _


class AuthorQuerySet(models.QuerySet):
    def managed_by(self, user):
        # NOTE: This will probably change in the future, if we implement
        # users' ability to control many authors. For now, we're assuming a
        # one-to-one relationship between the user and author. This function
        # currently exists to ease that transition, once it occurs.
        return self.filter(user=user)

    def by_initial(self, letter):
        # Authors whose first initial match the given letter, accounting for
        # culturally specific equivalents.

        implies = settings.ALPHABET['is']['implies']

        # Basic query, matching entries whose first letter matches the input.
        q = models.Q(name__istartswith=letter)

        if letter in implies:
            for equiv in implies[letter]:
                q |= models.Q(name__istartswith=equiv)

        return self.filter(q)

    def with_approved_poems(self):
        # Limits authors to those who have published poems and provides an
        # annotated value, `poem_count`, showing their number.
        return self.filter(
            poems__editorial_status='approved'
        ).annotate(
            poem_count=models.Count('poems')
        )


class PoemQuerySet(models.QuerySet):
    def managed_by(self, user):
        # NOTE: See note in `AuthorQuerySet.managed_by`.
        return self.filter(author__user=user)

    # Limits poems to those that are visible to the given user. Those are
    # poems that the user is the author of, and those that have been approved.
    def visible_to(self, user):
        # NOTE: See note in `AuthorQuerySet.managed_by`.
        if user.is_authenticated:
            return self.filter(
                Q(author__user=user)
                | Q(editorial_status='approved')
            )
        else:
            return self.filter(editorial_status='approved')

    def search(self, search_string):
        # TODO: This should probably become more sophisticated in the future.
        # For now, we replicate the functionality of the original website,
        # which is to check whether the search string occurs in its entirety
        # anywhere in the following fields:
        #
        # * Poem name
        # * Poem body
        # * Poem's about-field
        # * Author's name
        # * Author's name in the accusative
        # * Author's about-field

        return self.filter(
            models.Q(name__icontains=search_string)
            | models.Q(body__icontains=search_string)
            | models.Q(about__icontains=search_string)
            | models.Q(author__name__icontains=search_string)
            | models.Q(author__name_dative__icontains=search_string)
            | models.Q(author__about__icontains=search_string)
        )


class Author(models.Model):
    objects = AuthorQuerySet.as_manager()

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

    date_updated = models.DateTimeField(auto_now=True, null=True, blank=True)

    def __str__(self):
        if self.year_born is not None:
            return '%s (%d)' % (self.name, self.year_born)
        else:
            return self.name

    def get_absolute_url(self):
        return reverse('author', args=(self.id,))

    class Meta:
        ordering = ['name', 'year_born']


class Poem(models.Model):
    objects = PoemQuerySet.as_manager()

    EDITORIAL_STATUS_CHOICES = (

        # User is still working on poem.
        ('unpublished', _('Unpublished')),

        # User has trashed the poem.
        ('trashed', _('Trashed')),

        # User has published but poem is pending approval.
        ('pending', _('Pending approval')),

        # Poem has been reviewed and rejected by moderator.
        ('rejected', _('Rejected')),

        # Poem has been approved by moderator and is visible on website.
        ('approved', _('Approved')),

    )

    author = models.ForeignKey('poem.Author', related_name='poems', null=True, on_delete=models.CASCADE)

    # Poem contents.
    name = models.CharField(max_length=150, null=False, blank=False)
    body = models.TextField(null=False, blank=False)
    about = models.TextField(null=True, blank=True)

    # Editorial status.
    # NOTE: These should not be updated directly, but rather by using the
    # model's `set_editorial_status()`.
    editorial_status = models.CharField(max_length=20, choices=EDITORIAL_STATUS_CHOICES, default='unpublished')
    editorial_user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL)
    editorial_timing = models.DateTimeField(null=True, blank=True)
    editorial_reason = models.TextField(null=True, blank=True)

    date_created = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    date_updated = models.DateTimeField(auto_now=True, null=True, blank=True)

    # This function should be used to set `editorial_status` and related
    # fields. They should not be edited directly by the code.
    def set_editorial_status(self, editorial_status, editorial_user, editorial_reason=None):

        # Required for this to make sense.
        self.editorial_status = editorial_status
        self.editorial_user = editorial_user

        # Remember when this status was set.
        self.editorial_timing = timezone.now()

        # When no reason is given, and this function is called, we'll want to
        # reset the `editorial_reason` with the default None value. If a
        # reason is given, we'll want to store it, so this functions both for
        # remembering the reason and forgetting it when appropriate.
        self.editorial_reason = editorial_reason

    def __str__(self):
        return '%s - %s' % (self.name, self.author)

    def get_absolute_url(self):
        return reverse('poem', args=(self.id,))

    class Meta:
        ordering = ['-editorial_status', '-editorial_timing']


class DayPoem(models.Model):
    poem = models.ForeignKey('Poem', related_name='daypoems', on_delete=models.CASCADE)
    day = models.DateField()

    editorial_user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL)
    editorial_timing = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    class Meta:
        unique_together = ['poem', 'day']
        ordering = ['-editorial_timing', '-poem__editorial_timing']


class Bookmark(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='bookmarks', on_delete=models.CASCADE)
    poem = models.ForeignKey('poem.Poem', related_name='bookmarks', on_delete=models.CASCADE)

    class Meta:
        unique_together = ['user', 'poem']
