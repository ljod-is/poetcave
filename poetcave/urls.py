from poetcave.api import api
from django.contrib import admin
from django.urls import include
from django.urls import path

# Special treatment for reasons explained by the private-path URL config.
from poem.views import author

urlpatterns = [
    path("", include("core.urls")),
    path("", include("poem.urls")),
    path("", include("article.urls")),
    path("admin/", admin.site.urls),
    # This **must** come after **all** other paths, because otherwise a
    # private path that exists will override an existing system path, and a
    # private path that does not exist, will result in a 404 error for
    # anything that comes after this URL configuration. For example, if this
    # is placed before "/admin", then "/admin" will vanish into thin 404,
    # because it will be parsed as a private path that didn't match. Unless
    # of course there's an author with "author" as the private path, which
    # would mean they had effectively hijacked the admin section to present
    # wannabe-admins with poems instead.
    #
    # For this reason, this URL config is placed here instead of in the
    # `poem` app, even though that's what it organizationally belongs.
    path("<str:private_path>/", author, name="author_private_path"),
    path("api/", api.urls),
]
