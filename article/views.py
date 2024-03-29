from article.forms import ArticleForm
from article.models import Article
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.http import Http404
from django.shortcuts import redirect
from django.shortcuts import render
from django.urls import reverse
from django.utils import timezone


def articles(request):
    articles = Article.objects.visible_to(request.user)

    ctx = {
        "articles": articles,
    }
    return render(request, "article/list.html", ctx)


def article(request, article_id):
    try:
        article = Article.objects.visible_to(request.user).get(id=article_id)
    except Article.DoesNotExist:
        raise Http404

    ctx = {
        "article": article,
    }
    return render(request, "article/view.html", ctx)


@login_required
def article_add_edit(request, article_id=None):
    if not request.user.is_reporter:
        raise PermissionDenied

    if article_id is None:
        article = Article()
    else:
        article = Article.objects.get(id=article_id)

    form = ArticleForm(instance=article)

    if request.method == "POST":
        form = ArticleForm(request.POST, instance=article)
        if form.is_valid():
            with transaction.atomic():
                article = form.save()
                article.editorial_status = "unpublished"
                article.editorial_user = request.user
                article.editorial_timing = timezone.now()
                article.save()
            return redirect(reverse("article", kwargs={"article_id": article.id}))

    ctx = {
        "form": form,
    }
    return render(request, "article/control/add.html", ctx)


@login_required
def article_publish(request, article_id):
    if not request.user.is_reporter:
        raise PermissionDenied

    if request.method == "POST":
        editorial_status = request.POST.get("editorial_status", "")

        if editorial_status not in ["published", "unpublished"]:
            raise Exception(
                "Article editorial status must be either published or unpublished"
            )

        try:
            article = Article.objects.visible_to(request.user).get(id=article_id)
            article.editorial_status = editorial_status
            article.editorial_user = request.user
            article.editorial_timing = timezone.now()
            article.save()
            return redirect(reverse("article", kwargs={"article_id": article.id}))
        except Article.DoesNotExist:
            raise Http404
    else:
        raise Http404


@login_required
def article_delete(request, article_id):
    if not request.user.is_reporter:
        raise PermissionDenied

    if request.method == "POST":
        try:
            Article.objects.visible_to(request.user).get(id=article_id).delete()
        except Article.DoesNotExist:
            raise Http404
    else:
        raise Http404

    return redirect(reverse("articles"))
