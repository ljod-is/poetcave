from django.urls import path
from poem import views

# NOTE/TODO: `author_id` is used extensively here. We should change this to
# `author_slug` once we have feature compatibility with the existing website.
# It requires us to implement a slug-mechanism, though.

urlpatterns = [
    path('poem/<int:poem_id>/', views.poem, name='poem'),
    path('poems/newest/', views.poems_newest, name='poems_newest'),
    path('poems/daypoems/<int:year>/', views.poems_daypoems, name='poems_daypoems'),
    path('poems/daypoems/', views.poems_daypoems, name='poems_daypoems'),
    path('poems/by-author/<str:letter>/', views.poems_by_author, name='poems_by_author'),
    path('poems/by-author/', views.poems_by_author, name='poems_by_author'),
    path('poems/search/', views.poems_search, name='poems_search'),
    path('poems/<str:listing_type>/', views.poems, name='poems'),
    path('poems/', views.poems, name='poems'),
    path('author/<int:author_id>/admin/', views.author_admin, name='author_admin'),
    path('author/<int:author_id>/poem/add/', views.poem_add_edit, name='poem_add'),
    path('author/<int:author_id>/poem/edit/<int:poem_id>/', views.poem_add_edit, name='poem_edit'),
    path('author/<int:author_id>/poem/delete/<int:poem_id>/', views.poem_delete, name='poem_delete'),
    path('author/<int:author_id>/poem/publish/<int:poem_id>/', views.poem_publish, name='poem_publish'),
    path('author/<int:author_id>/poem/unpublish/<int:poem_id>/', views.poem_unpublish, name='poem_unpublish'),
    path('author/<int:author_id>/poem/untrash/<int:poem_id>/', views.poem_untrash, name='poem_untrash'),
    path('author/<int:author_id>/', views.author, name='author'),
    path('bookmarks/', views.bookmarks, name='bookmarks'),
    path('bookmark/add/<int:poem_id>/', views.bookmark_add, name='bookmark_add'),
    path('bookmark/delete/<int:poem_id>/', views.bookmark_delete, name='bookmark_delete'),
]
