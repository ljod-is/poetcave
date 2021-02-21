from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.shortcuts import redirect
from django.shortcuts import render
from django.urls import reverse
from poem.forms import PoemForm
from poem.models import Author
from poem.models import Poem

# NOTE: In the future, it may become possible for a user to have access to multiple
# authors, for example deceased authors whose works have fallen out of copyright.
# Therefore, we should rely on an `author` object in these views rather than
# `request.user.author`, since the latter may become irrelevant in the future.

# NOTE: These views take an `author_id` parameter when dealing with authors. Once we
# are feature-complete with respect to the existing websites, we should change this to
# `author_slug` after having implemented a slug mechanism for authors.

@login_required
def author_admin(request, author_id):

    try:
        author = Author.objects.managed_by(request.user).get(id=author_id)
    except Author.DoesNotExist:
        raise Http404

    ctx = {
        'author': author,
    }
    return render(request, 'author/admin.html', ctx)


@login_required
def poem_add_edit(request, author_id, poem_id=None):

    try:
        author = Author.objects.managed_by(request.user).get(id=author_id)
    except Author.DoesNotExist:
        raise Http404

    if poem_id is not None:
        poem = Poem.objects.managed_by(request.user).get(id=poem_id)
    else:
        poem = Poem()

    form = PoemForm(instance=poem)
    if request.method == 'POST':
        form = PoemForm(request.POST, instance=poem)
        if form.is_valid():
            poem = form.save(commit=False)
            poem.author_id = author.id
            poem.save()
            return redirect(reverse('author_admin', args=(author.id,)))

    ctx = {
        'author': author,
        'form': form,
    }
    return render(request, 'poem/add.html', ctx)


@login_required
def poem_delete(request, author_id, poem_id):

    author = Author.objects.managed_by(request.user).get(id=author_id)
    poem = Poem.objects.managed_by(request.user).get(id=poem_id)

    if request.method == 'POST':
        poem.delete()
        return redirect(reverse('author_admin', args=(author.id,)))

    ctx = {
        'author': author,
        'poem': poem,
    }
    return render(request, 'poem/delete.html', ctx)


def poems(request, listing_type=None, argument=None):

    # Supported listing types.
    supported_listing_types = [
        'newest',
        'previous-daypoems',
        'by-author'
    ]

    # Sane defaults.
    if listing_type is None:
        # We don't like two URLs spouting the same content, so we'll redirect
        # to the first supported listing type instead of setting the
        # listing_type in code and continuing.
        return redirect(reverse('poems', args=(supported_listing_types[0],)))

    # Sanitize input.
    if listing_type not in supported_listing_types:
        raise Http404

    # Get poems depending on listing type and optional arguments.
    poems = []
    if listing_type == 'newest':
        poems = Poem.objects.filter(
            editorial_status='approved'
        ).order_by(
            '-editorial_timing',
            '-public_timing'
        )[:25]

    ctx = {
        'NEWEST_COUNT': settings.NEWEST_COUNT,
        'listing_type': listing_type,
        'poems': poems,
    }
    return render(request, 'poem/poems.html', ctx)
