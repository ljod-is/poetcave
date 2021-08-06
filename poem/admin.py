from django.contrib import admin
from django.utils.translation import ugettext as _
from .models import Author
from .models import Poem


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    pass


@admin.register(Poem)
class PoemAdmin(admin.ModelAdmin):
    list_display = ['name', 'author', 'editorial_status']
    list_filter = ['editorial_status']
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
        [_('User decisions'), {
            'fields': [
                'public',
                'public_timing',
                'trashed',
                'trashed_timing'
            ]
        }],
        [_('Editorial'), {
            'fields': [
                'editorial_status',
                'editorial_user',
                'editorial_timing',
                'editorial_reason',
            ],
        }],
    ]
