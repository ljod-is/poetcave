from django.contrib import admin
from django.utils.translation import ugettext as _
from .models import Author
from .models import Poem


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    pass


@admin.register(Poem)
class PoemAdmin(admin.ModelAdmin):
    list_display = ['name', 'author', 'editorial']
    list_filter = ['editorial__status']
    search_fields = ['name', 'body', 'about', 'author__name']
    fieldsets = [
        [_('Material'), {
            'fields': [
                'name',
                'body',
                'about',
                'author'
            ],
        }],
    ]

    def get_queryset(self, request):
        return super(PoemAdmin, self).get_queryset(request).select_related(
            'author',
            'editorial'
        )
