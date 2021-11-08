from article.models import Article
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.shortcuts import render

def articles(request):

    articles = Article.objects.visible_to(request.user)

    ctx = {
        'articles': articles,
    }
    return render(request, 'article/list.html', ctx)


def article(request, article_id):

    try:
        article = Article.objects.visible_to(request.user).get(id=article_id)
    except Article.DoesNotExist:
        raise Http404

    ctx = {
        'article': article,
    }
    return render(request, 'article/view.html', ctx)
