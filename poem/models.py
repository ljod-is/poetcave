from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils.translation import ugettext as _


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

    def with_publicly_visible_poems(self):
        # Limits authors to those who have published poems and provides an
        # annotated value, `poem_count`, showing their number.
        return self.filter(
            poems__editorial_status='approved',
            poems__public=True,
            poems__trashed=False
        ).annotate(
            poem_count=models.Count('poems')
        )


class PoemQuerySet(models.QuerySet):
    def managed_by(self, user):
        # NOTE: See note in `AuthorQuerySet.managed_by`.
        return self.filter(author__user=user)

    def publicly_visible(self):
        # Poems fulfilling all conditions for a poem to be publicly visible.
        return self.filter(
            editorial_status='approved',
            public=True,
            trashed=False
        )

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
        ('pending', _('Pending')),
        ('approved', _('Approved')),
        ('rejected', _('Rejected')),
    )

    author = models.ForeignKey('poem.Author', related_name='poems', null=True, on_delete=models.CASCADE)

    # Poem contents.
    name = models.CharField(max_length=150, null=False, blank=False)
    body = models.TextField(null=False, blank=False)
    about = models.TextField(null=True, blank=True)

    # User decisions.
    public = models.BooleanField(default=False)
    public_timing = models.DateTimeField(null=True, blank=True)
    trashed = models.BooleanField(default=False)
    trashed_timing = models.DateTimeField(null=True, blank=True)

    # Editorial decision.
    editorial_status = models.CharField(max_length=20, choices=EDITORIAL_STATUS_CHOICES, default='pending')
    editorial_user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL)
    editorial_timing = models.DateTimeField(null=True, blank=True)
    editorial_reason = models.TextField(null=True, blank=True)

    # `date_joined` field for creation is provided by parent model.
    date_created = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    date_updated = models.DateTimeField(auto_now=True, null=True, blank=True)

    def __str__(self):
        return '%s - %s' % (self.name, self.author)

    def get_absolute_url(self):
        return reverse('poem', args=(self.id,))

    class Meta:
        ordering = ['-editorial_timing', '-public_timing']
