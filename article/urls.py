from django.urls import path

from article import views

urlpatterns = [
    path('article/add/', views.article_add_edit, name='article_add'),
    path('article/edit/<int:article_id>/', views.article_add_edit, name='article_edit'),
    path('article/delete/<int:article_id>/', views.article_delete, name='article_delete'),
    path('article/<int:article_id>', views.article, name='article'),
    path('articles/', views.articles, name='articles'),
]
