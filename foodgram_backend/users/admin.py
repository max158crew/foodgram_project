from django.contrib import admin

from .models import Follow, User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):

    list_display = ("username", "email", "first_name", "last_name")
    list_display_links = ("username",)
    search_fields = (
        "username",
    )
    list_filter = (
        "username",
        "email",
    )


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):

    list_display = (
        "user",
        "author",
    )
    list_display_links = ("user",)
    search_fields = (
        "user",
        "author",
    )
    list_filter = ("user",)
