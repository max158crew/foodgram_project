from django.contrib import admin

from .models import (Favorite, Ingredient, IngredientRecipe, Recipe,
                     ShoppingCart, Tag)


class IngredientsRecipeAdmin(admin.TabularInline):
    model = IngredientRecipe


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """
    Панель админа для редактирования набора тегов
    """

    list_display = (
        "name",
        "color",
        "slug",
    )
    list_display_links = ("name",)
    search_fields = ("name",)
    list_filter = ("name",)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """
    Панель администратора для редактирования Ингредиентов
    """

    list_display = (
        "id",
        "name",
        "measurement_unit",
    )
    list_display_links = ("name",)
    search_fields = ("name",)
    list_filter = ("name",)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "author",
        "in_favorited",
        "pub_date",
    )
    list_display_links = ("name",)
    search_fields = ("name",)
    list_filter = (
        "name",
        "author",
    )
    readonly_fields = ("in_favorited",)
    filter_horizontal = ("tags",)
    inlines = (IngredientsRecipeAdmin,)

    def in_favorited(self, obj):
        return obj.in_favorited.all().count()


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    """
    Панель админа для редактирования избранного
    """

    list_display = (
        "user",
        "recipe",
    )
    search_fields = (
        "user",
        "recipe",
    )
    list_filter = ("recipe",)


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    """
    Панель админа для редактирования списка покупок
    """

    list_display = (
        "user",
        "recipe",
    )
    search_fields = (
        "user",
        "recipe",
    )
    list_filter = (
        "user",
        "recipe",
    )
