from datetime import timedelta
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.forms import ValidationError
from django.http import Http404
from django.shortcuts import redirect
from django.shortcuts import render
from django.urls import reverse
from django.utils import timezone
from poem.forms import PoemForm
from poem.models import Author
from poem.models import Bookmark
from poem.models import DayPoem
from poem.models import Poem

# NOTE: In the future, it may become possible for a user to have access to multiple
# authors, for example deceased authors whose works have fallen out of copyright.
# Therefore, we should rely on an `author` object in these views rather than
# `request.user.author`, since the latter may become irrelevant in the future.

# NOTE: These views take an `author_id` parameter when dealing with authors. Once we
# are feature-complete with respect to the existing websites, we should change this to
# `author_slug` after having implemented a slug mechanism for authors.

@login_required
def poem_add_edit(request, author_id=None, poem_id=None):

    # If adding a poem...
    if author_id is not None:
        try:
            author = Author.objects.managed_by(request.user).get(id=author_id)
        except Author.DoesNotExist:
            raise PermissionDenied

        poem = Poem()
        poem.author_id = author.id
    # If editing a poem...
    elif poem_id is not None:
        poem = Poem.objects.select_related('author').managed_by(request.user).get(id=poem_id)

        # Needed to consistently send the author to the template regardless of
        # whether we're adding oer editing.
        author = poem.author

        # We retain these for checking if the name or body have been updated.
        # We need this information later to determine whether to change the
        # editorial status as a result of a previous rejection.
        old_name = poem.name
        old_body = poem.body
    else:
        # Urlconf shouldn't let this happen.
        raise Http404


    form = PoemForm(instance=poem)
    if request.method == 'POST':
        form = PoemForm(request.POST, instance=poem)
        if form.is_valid():

            with transaction.atomic():

                # First, save the poem.
                poem = form.save()

                # The editorial status should automatically be set to
                # "unpublished" in two situations.
                #
                # 1. As the default editorial status for a new poem.
                #
                # 2. If the poem was previously rejected, but the user is now
                # editing the content. That way, the user can try publishing
                # it after having edited it according to the message
                # accompanying the rejection.
                if (poem.editorial is None
                    or (
                        poem.editorial.status == 'rejected'
                        and (
                            old_name != poem.name
                            or old_body != poem.body
                        )
                    )
                ):
                    poem.set_editorial_status('unpublished', request.user)

            # Redirect to poem.
            return redirect(reverse('poem', args=(poem.id,)))

    ctx = {
        'author': author,
        'form': form,
    }
    return render(request, 'poem/control/add.html', ctx)


@login_required
def poem_delete(request, poem_id):

    poem = Poem.objects.managed_by(request.user).get(id=poem_id)

    if request.method == 'POST':
        author_id = poem.author_id
        poem.delete()
        return redirect(reverse('author', args=(author_id,)))

    ctx = {
        'poem': poem,
    }
    return render(request, 'poem/control/delete.html', ctx)


@login_required
def poem_publish(request, poem_id):

    try:
        poem = Poem.objects.managed_by(request.user).get(id=poem_id)
    except Poem.DoesNotExist:
        raise PermissionDenied

    if poem.editorial.status == 'unpublished':
        poem.set_editorial_status('pending', request.user)
        poem.save()

    return redirect(reverse('poem', args=(poem_id,)))


@login_required
def poem_unpublish(request, poem_id):

    try:
        poem = Poem.objects.managed_by(request.user).get(id=poem_id)
    except Poem.DoesNotExist:
        raise PermissionDenied

    if request.method == 'POST':
        if poem.editorial.status in ['pending', 'approved']:
            poem.set_editorial_status('unpublished', request.user)
            poem.save()

            return redirect(reverse('poem', args=(poem_id,)))

    ctx = {
        'poem': poem,
    }

    return render(request, 'poem/control/unpublish.html', ctx)


@login_required
def poem_untrash(request, poem_id):

    try:
        poem = Poem.objects.managed_by(request.user).get(id=poem_id)
    except Poem.DoesNotExist:
        raise PermissionDenied

    if poem.editorial.status == 'trashed':
        poem.set_editorial_status('unpublished', request.user)
        poem.save()

    return redirect(reverse('poem', args=(poem_id,)))


@login_required
def bookmarks(request):

    bookmarks = Bookmark.objects.select_related(
        'poem'
    ).filter(
        user_id=request.user.id,
        poem__editorial__status='approved'
    )

    ctx = {
        'bookmarks': bookmarks,
    }
    return render(request, 'bookmark/bookmarks.html', ctx)


@login_required
def bookmark_add(request, poem_id):

    try:
        poem = Poem.objects.get(id=poem_id, editorial__status='approved')
    except Poem.DoesNotExist:
        raise Http404

    Bookmark.objects.get_or_create(
        user=request.user,
        poem=poem
    )

    return redirect(reverse('bookmarks'))


@login_required
def bookmark_delete(request, poem_id):
    try:
        Bookmark.objects.get(
            user_id=request.user.id,
            poem_id=poem_id
        ).delete()
    except Poem.DoesNotExist:
        raise Http404

    return redirect(reverse('bookmarks'))


def author(request, author_id):
    try:
        author = Author.objects.get(id=author_id)
    except Author.DoesNotExist:
        raise Http404

    poems = Poem.objects.visible_to(request.user).filter(author_id=author_id)

    ctx = {
        'author': author,
        'poems': poems,
    }
    return render(request, 'poem/author.html', ctx)


def poems_newest(request):
    poems = Poem.objects.select_related('author').filter(editorial__status='approved')[:25]

    ctx = {
        'poems': poems,
        'listing_type': 'newest',
    }
    return render(request, 'poem/poems.html', ctx)


def poems_daypoems(request, year=None):

    # Get the years in which there were daypoems.
    years = [d.year for d in DayPoem.objects.dates('day', 'year')]

    # Redirect to the most recently available year if we don't have anything
    # specified, to reflect the location properly in the URL.
    if year is None:
        return redirect(reverse('poems_daypoems', args=[years[-1]]))

    # Make sure that we have the requested year.
    if year not in years:
        raise Http404

    # Find beginning and end of year.
    today = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
    year_begin = today.replace(year=year, month=1, day=1)
    year_end = year_begin.replace(year=year+1) - timedelta(seconds=1)

    # Get daypoems of the selected year, prefetching poems.
    daypoems = DayPoem.objects.prefetch_related('poem').filter(
        poem__editorial__status='approved',
        day__gte=year_begin,
        day__lte=year_end
    )

    ctx = {
        'years': years,
        'year': year,
        'daypoems': daypoems,
        'listing_type': 'daypoems',
    }
    return render(request, 'poem/poems.html', ctx)


def poems_by_author(request, letter=None):

    # Short-hands.
    letters = settings.ALPHABET[settings.LANGUAGE_CODE]['letters']

    # Default to first letter.
    if letter is None:
        return redirect(reverse('poems_by_author', args=(letters[0],)))

    # Sanitize input.
    if letter not in letters:
        raise Http404

    authors = Author.objects.with_approved_poems().by_initial(
        letter
    ).order_by(
        'name'
    )

    ctx = {
        'letters': letters,
        'authors': authors,
        'listing_type': 'by-author',
    }
    return render(request, 'poem/poems.html', ctx)


def poems_search(request):

    search_string = request.GET.get('q', '')

    poems = Poem.objects.select_related(
        'author'
    ).filter(
        editorial__status='approved'
    ).search(
        search_string
    )

    ctx = {
        'poems': poems,
        'search_string': search_string,
        'listing_type': 'search',
    }
    return render(request, 'poem/poems.html', ctx)


@login_required
def poems_moderate(request, poem_id=None):
    if not request.user.is_moderator:
        raise PermissionDenied

    if request.method == 'POST':
        poem_id = request.POST.get('poem_id', None)
        status = request.POST.get('status', None)

        # Manage `poem_id`, making sure it's a proper ID (and an integer).
        try:
            poem = Poem.objects.get(id=int(poem_id), editorial__status='pending')
        except Poem.DoesNotExist:
            # This will only happen when requesting a poem that does not
            # exist, or one that has been handled by another moderator by
            # coincidence in the time period it took this moderator to read
            # it over and decide. In either case, we'll want to simply reload
            # the page and fetch a new random poem to moderate.
            return redirect(reverse('poems_moderate'))
        except:
            # It basically doesn't matter what goes wrong here; it will be
            # because there is something wrong with the ID.
            raise ValidationError('poem_id must be a valid ID of a poem pending approval.')

        if status == 'approved':
            # Yay! A new poem on our website! \o/
            poem.set_editorial_status('approved', request.user)
        elif status == 'rejected':
            # Hopefully the reason is good.
            reason = request.POST.get('reason', '')
            poem.set_editorial_status('rejected', request.user, reason)
        else:
            raise ValidationError('Invalid status received.')

        # Redirect so that browser won't want to re-post on reload.
        return redirect(reverse('poems_moderate'))

    poems = poem = Poem.objects.filter(
        editorial__status='pending'
    ).exclude(
        author=None
    ).select_related(
        'author'
    )

    # Moderators may pick a specific poem to moderate, for example by
    # request, but are otherwise given one at random.
    if poem_id is not None:
        try:
            poem = poems.get(id=poem_id)
        except Poem.DoesNotExist:
            raise Http404
    else:
        # The randomness factor is to reduce the likelyhood of two moderators
        # working on the same poem at the same time.
        poem = poems.order_by('?').first()

    ctx = {
        'poem_count': poems.count(),
        'poem': poem,
    }
    return render(request, 'poem/moderate.html', ctx)


def poems(request):
    return redirect(reverse('poems_newest'))


def poem(request, poem_id):
    try:
        # The specific poem being requested.
        poem = Poem.objects.select_related('author').visible_to(request.user).get(id=poem_id)
    except Poem.DoesNotExist:
        raise Http404

    # Other poems by the same author.
    poems = poem.author.poems.visible_to(request.user)

    ctx = {
        'poem': poem,
        'poems': poems,
    }
    return render(request, 'poem/poem.html', ctx)
