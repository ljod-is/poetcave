from django.urls import path

from article import views

urlpatterns = [
    path('article/<int:article_id>', views.article, name='article'),
    path('articles/', views.articles, name='articles'),
]
