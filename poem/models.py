from django.conf import settings
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models
from django.db import transaction
from django.db.models import Prefetch
from django.db.models import Q
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django_mdmail import send_mail


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
            poems__editorial__status='approved'
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
                | Q(editorial__status='approved')
            )
        else:
            return self.filter(editorial__status='approved')

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

    # A unique, private path for VIPs. Set by administrator.
    # Example: https://poetcave.org/john-smith
    private_path = models.CharField(max_length=150, unique=True, null=True, blank=True, validators=[UnicodeUsernameValidator()])

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
    user = models.OneToOneField('core.User', null=True, blank=True, related_name='author', on_delete=models.SET_NULL)

    date_updated = models.DateTimeField(auto_now=True, null=True, blank=True)

    def __str__(self):
        if self.year_born is not None:
            return '%s (%d)' % (self.name, self.year_born)
        else:
            return self.name

    def get_absolute_url(self):
        if self.private_path is not None:
            return reverse('author_private_path', kwargs={'private_path': self.private_path})
        else:
            return reverse('author', kwargs={'author_id': self.id})

    class Meta:
        ordering = ['name', 'year_born']


class Poem(models.Model):
    objects = PoemQuerySet.as_manager()

    author = models.ForeignKey('poem.Author', related_name='poems', null=True, on_delete=models.CASCADE)

    # Poem contents.
    name = models.CharField(max_length=150, null=False, blank=False)
    body = models.TextField(null=False, blank=False)
    about = models.TextField(null=True, blank=True)

    # Current editorial status. Note that the `editorial_history` is produced
    # by the foreign key to `poem` in the EditorialDecision model. This should
    # always be the newest object found in `editorial_history`, and is here
    # for convenience, so that we don't constantly have to deal with a long
    # list of objects when we almost always only care about the newest entry.
    #
    # NOTE: This should not be updated directly, but rather by using the
    # model's `set_editorial_status()`.
    editorial = models.OneToOneField('EditorialDecision', related_name='current_poem', null=True, on_delete=models.SET_NULL)

    date_created = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    date_updated = models.DateTimeField(auto_now=True, null=True, blank=True)

    # This function should be used to set `editorial` and populate
    # `editorial_history` on a `poem`.
    def set_editorial_status(self, editorial_status, editorial_user, editorial_reason=None):

        editorial = EditorialDecision()

        editorial.status = editorial_status
        editorial.user = editorial_user
        editorial.timing = timezone.now()
        editorial.reason = editorial_reason

        with transaction.atomic():
            # Save te editorial decision, so that it becomes of the history,
            # linked to `editorial_history` on the `poem`'s side.
            editorial.poem = self
            editorial.save()

            # Save the editorial decision as the current one to the `poem`,
            # for easy access.
            self.editorial = editorial
            self.save()

        # Notify user about decision.
        self.explain_editorial_decision_by_mail()

    def explain_editorial_decision_by_mail(self):
        # NOTE: This assumes only one user per author. See Author model.
        recipients = [self.author.user.email]

        # TODO: Flagrantly violating DRY here. Not worth convoluting yet.
        if self.editorial.status == 'rejected':
            subject = render_to_string('poem/mail/poem_rejected_subject.txt', {'poem': self}).replace('\n', '').replace('\r', '')
            message = render_to_string('poem/mail/poem_rejected.md', {'poem': self})
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, recipients)
        elif self.editorial.status == 'approved':
            subject = render_to_string('poem/mail/poem_approved_subject.txt', {'poem': self}).replace('\n', '').replace('\r', '')
            message = render_to_string('poem/mail/poem_approved.md', {'poem': self})
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, recipients)

    def __str__(self):
        return '%s - %s' % (self.name, self.author)

    def get_absolute_url(self):
        return reverse('poem', args=(self.id,))

    class Meta:
        ordering = ['-editorial__status', '-editorial__timing']


class DayPoem(models.Model):
    poem = models.ForeignKey('Poem', related_name='daypoems', on_delete=models.CASCADE)
    day = models.DateField(blank=True)

    editorial_user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL)
    editorial_timing = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    class Meta:
        unique_together = ['poem', 'day']
        ordering = ['-editorial_timing', '-poem__editorial__timing']


class Bookmark(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='bookmarks', on_delete=models.CASCADE)
    poem = models.ForeignKey('poem.Poem', related_name='bookmarks', on_delete=models.CASCADE)

    class Meta:
        unique_together = ['user', 'poem']


class EditorialDecision(models.Model):
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

    poem = models.ForeignKey('poem.Poem', related_name='editorial_history', on_delete=models.CASCADE)

    status = models.CharField(max_length=20, choices=EDITORIAL_STATUS_CHOICES, default='unpublished')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL)
    timing = models.DateTimeField(null=True, blank=True)
    reason = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.get_status_display()

    class Meta:
        ordering = ['-timing']
