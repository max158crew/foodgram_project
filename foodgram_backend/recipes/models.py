from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, RegexValidator

from colorfield.fields import ColorField
from users.models import User

# User = get_user_model()



class Tag(models.Model):
    """
    Модель тегов
    """
    name_validator = RegexValidator(
        regex=r'^[a-zA-Z0-9_а-яА-Я]+$',
        message='Разрешены только буквы, цифры и символ подчеркивания',
        code='invalid_tag_name'
    )

    color_validator = RegexValidator(
        regex=r'^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$',
        message='Значение должно быть в формате HEX (например, #FF0000)',
        code='invalid_color_code'
    )

    name = models.CharField(
        max_length=100,
        validators=[name_validator]
        )
    color = ColorField(format="hex",
                       validators=[color_validator]
                       )
    slug = models.SlugField(verbose_name="Slug", unique=True)

    class Meta:
        ordering = ("-name",)

    def __str__(self):
        return self.slug

class Ingredient(models.Model):

    name = models.CharField(
        max_length=200, db_index=True)
    measure = models.CharField(
        max_length=60)


    def __str__(self):
        return f"{self.name}, {self.measure}"

class Recipe(models.Model):
    name = models.CharField(
        max_length=200,
        verbose_name="Название",
    )
    author = models.ForeignKey(
        User, related_name='recipes', on_delete=models.CASCADE
    )
    text = models.TextField()
    ingredients = models.ManyToManyField(Ingredient, through='IngredientRecipe')
    image = models.ImageField(blank=True, upload_to="recipes/images")
    tags = models.ManyToManyField(
        Tag,
        verbose_name="Тэги",
    )
    pub_date = models.DateTimeField(
        verbose_name="Дата публикации", auto_now_add=True)
    cooking_time = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(
            1, message="Время не должно быть менее 1 минуты!")]
    )

    class Meta:
        ordering = ("-pub_date",)

    def __str__(self):
        return self.name

class IngredientRecipe(models.Model):
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    amount = models.FloatField(
        default=1,
        validators=[MinValueValidator(
            0.01, message="Ингредиента должно быть больше 0.01!")])

    def __str__(self):
        return f"{self.recipe}: {self.ingredient} – {self.amount}"

class Cart(models.Model):


    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
    )


class Favorite(models.Model):

    recipe = models.ForeignKey(
        Recipe,
        related_name="in_favorited",
        on_delete=models.CASCADE,
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
    )
    class Meta:
        ordering = ("user",)

class Favorite(models.Model):

    recipe = models.ForeignKey(
        Recipe,
        related_name="in_favorited",
        on_delete=models.CASCADE,
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
    )

    class Meta:
        ordering = ("user",)
        default_related_name = "favorite"
        verbose_name = "Избранный рецепт"
        verbose_name_plural = "Избранное"
        constraints = [models.UniqueConstraint(
            fields=["recipe", "user"], name="unique_favorite")]

class ShoppingCart(models.Model):

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
    )

    class Meta:
        default_related_name = "shopping_cart"
        verbose_name = "Рецепт в списке покупок"
        verbose_name_plural = "Список покупок"
        constraints = [models.UniqueConstraint(
            fields=["user", "recipe"], name="unique_shopping_cart")]


