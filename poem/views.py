from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from poem.models import Author

@login_required
def author_admin(request, author_id):
    # NOTE: In the future, it may become possible for a user to have access
    # to multiple authors, for example deceased authors whose works have
    # fallen out of copyright. Therefore, we should rely on the `author`
    # object in this view rather than `request.user.author`, since the latter
    # may become irrelevant in the future.

    if request.user.author_id != author_id:
        raise PermissionDenied()

    author = get_object_or_404(Author, id=author_id, user=request.user)

    ctx = {
        'author': author,
    }
    return render(request, 'author/admin.html', ctx)
