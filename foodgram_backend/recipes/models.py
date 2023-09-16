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
        verbose_name="Название тэга",
        validators=[name_validator]
        )
    color = ColorField(format="hex",
                       verbose_name="Цветовой код",
                       validators=[color_validator]
                       )
    slug = models.SlugField(verbose_name="Slug", unique=True)

    class Meta:
        ordering = ("-name",)
        verbose_name = "Тэг"
        verbose_name_plural = "Тэги"

    def __str__(self):
        return self.slug

class Ingredient(models.Model):
    name = models.CharField(max_length=128)
    measure = models.CharField(max_length=64)

    def __str__(self):
        return self.name

class Recipe(models.Model):
    name = models.CharField(
        max_length=200,
        verbose_name="Название рецепта",
    )
    owner = models.ForeignKey(
        User, related_name='recipes', on_delete=models.CASCADE
    )
    text = models.TextField()
    ingredients = models.ManyToManyField(Ingredient, through='IngredientRecipe')

    def __str__(self):
        return self.name

class IngredientRecipe(models.Model):
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.ingredient} {self.recipe}'

class Cart(models.Model):
    pass

class Favorite(models.Model):
    pass

