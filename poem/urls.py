from django.urls import path
from poem import views

# NOTE/TODO: `author_id` is used extensively here. We should change this to
# `author_slug` once we have feature compatibility with the existing website.
# It requires us to implement a slug-mechanism, though.

urlpatterns = [
    path('author/<int:author_id>/admin/', views.author_admin, name='author_admin'),
    path('author/<int:author_id>/poem/add/', views.poem_add_edit, name='poem_add'),
    path('author/<int:author_id>/poem/edit/<int:poem_id>/', views.poem_add_edit, name='poem_edit'),
    path('author/<int:author_id>/poem/delete/<int:poem_id>/', views.poem_delete, name='poem_delete'),
]
