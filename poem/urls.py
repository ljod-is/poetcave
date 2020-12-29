from django.urls import path
from poem import views

# NOTE/TODO: `author_id` is used extensively here. We should change this to
# `author_slug` once we have feature compatibility with the existing website.
# It requires us to implement a slug-mechanism, though.

urlpatterns = [
    path('author/<int:author_id>/admin/', views.author_admin, name='author_admin'),
]
