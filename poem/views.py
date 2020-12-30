from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render
from django.urls import reverse
from poem.forms import PoemForm
from poem.models import Author

# NOTE: In the future, it may become possible for a user to have access to multiple
# authors, for example deceased authors whose works have fallen out of copyright.
# Therefore, we should rely on an `author` object in these views rather than
# `request.user.author`, since the latter may become irrelevant in the future.

# NOTE: These views take an `author_id` parameter when dealing with authors. Once we
# are feature-complete with respect to the existing websites, we should change this to
# `author_slug` after having implemented a slug mechanism for authors.

@login_required
def author_admin(request, author_id):

    if request.user.author_id != author_id:
        raise PermissionDenied()

    author = get_object_or_404(Author, id=author_id, user=request.user)

    ctx = {
        'author': author,
    }
    return render(request, 'author/admin.html', ctx)


@login_required
def poem_add(request, author_id):

    if request.user.author_id != author_id:
        raise PermissionDenied()

    author = get_object_or_404(Author, id=author_id, user=request.user)

    form = PoemForm()
    if request.method == 'POST':
        form = PoemForm(request.POST)
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
