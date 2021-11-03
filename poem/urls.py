from django.urls import path
from poem import views

# NOTE/TODO: `author_id` is used extensively here. We should change this to
# `author_slug` once we have feature compatibility with the existing website.
# It requires us to implement a slug-mechanism, though.

urlpatterns = [
    path('poem/add/author/<int:author_id>/', views.poem_add_edit, name='poem_add'),
    path('poem/edit/<int:poem_id>/', views.poem_add_edit, name='poem_edit'),
    path('poem/delete/<int:poem_id>/', views.poem_delete, name='poem_delete'),
    path('poem/publish/<int:poem_id>/', views.poem_publish, name='poem_publish'),
    path('poem/unpublish/<int:poem_id>/', views.poem_unpublish, name='poem_unpublish'),
    path('poem/untrash/<int:poem_id>/', views.poem_untrash, name='poem_untrash'),
    path('poem/<int:poem_id>/', views.poem, name='poem'),
    path('poems/author/<int:author_id>/', views.author, name='author'),
    path('poems/moderate/<int:poem_id>/', views.poems_moderate, name='poems_moderate'),
    path('poems/moderate/', views.poems_moderate, name='poems_moderate'),
    path('poems/newest/', views.poems_newest, name='poems_newest'),
    path('poems/daypoems/<int:year>/', views.poems_daypoems, name='poems_daypoems'),
    path('poems/daypoems/', views.poems_daypoems, name='poems_daypoems'),
    path('poems/daypoem/set/<int:poem_id>/', views.poem_set_daypoem, name='poem_set_daypoem'),
    path('poems/by-author/<str:letter>/', views.poems_by_author, name='poems_by_author'),
    path('poems/by-author/', views.poems_by_author, name='poems_by_author'),
    path('poems/search/', views.poems_search, name='poems_search'),
    path('poems/<str:listing_type>/', views.poems, name='poems'),
    path('poems/', views.poems, name='poems'),
    path('bookmarks/', views.bookmarks, name='bookmarks'),
    path('bookmark/add/<int:poem_id>/', views.bookmark_add, name='bookmark_add'),
    path('bookmark/delete/<int:poem_id>/', views.bookmark_delete, name='bookmark_delete'),
]
