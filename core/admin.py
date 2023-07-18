from django.contrib import admin
from django.contrib.auth.models import Group
from .models import User

admin.site.unregister(Group)


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = [
        "username",
        "author",
        "email",
        "contact_name",
        "is_moderator",
        "is_superuser",
    ]
    search_fields = ["username", "author__name", "email", "contact_name"]
