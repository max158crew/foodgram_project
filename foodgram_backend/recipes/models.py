from colorfield.fields import ColorField
from django.db import models
from django.core.validators import MinValueValidator, RegexValidator

from users.models import User


class Tag(models.Model):
    """
    Модель тэгов для рецептов.

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
        verbose_name='Название тэга',
        validators=[name_validator])
    color = ColorField(format='hex',
                       verbose_name='Цвет тэга',
                       validators=[color_validator])
    slug = models.SlugField(verbose_name='Slug', unique=True)

    class Meta:
        ordering = ('-name',)
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'

    def __str__(self):
        return self.slug


class Ingredient(models.Model):
    """
    Модель ингредиентов для рецепта.
    """

    name = models.CharField(verbose_name='Название Ингредиента',
                            max_length=200, db_index=True)
    measurement_unit = models.CharField(verbose_name='Единица измерения',
                                        max_length=60)

    def __str__(self):
        return f"{self.name}, {self.measurement_unit}"

    class Meta:
        ordering = ('-name',)
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'


class Recipe(models.Model):
    """
    Модель рецептов.
    """
    name = models.CharField(
        max_length=200,
        verbose_name="Название",
    )
    author = models.ForeignKey(
        User, related_name='recipes',
        on_delete=models.CASCADE,
        verbose_name="Автор рецепта",
    )
    text = models.TextField(verbose_name='Описание рецепта')
    ingredients = models.ManyToManyField(Ingredient,
                                         through='IngredientRecipe',
                                         blank=False,
                                         verbose_name='Ингредиенты')
    image = models.ImageField(blank=True,
                              upload_to='recipes/images',
                              verbose_name='Фото рецепта')
    tags = models.ManyToManyField(Tag,
                                  blank=False,
                                  verbose_name='Тэги рецепта')
    pub_date = models.DateTimeField(
        verbose_name="Дата публикации",
        auto_now_add=True)
    cooking_time = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(
            1, message='Время не должно быть менее 1 минуты!')],
        verbose_name='Время приготовления'
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class IngredientRecipe(models.Model):
    """Количество ингредиентов в блюде.
        Модель связывает Recipe и Ingredient
        с указанием количества ингредиента.
    """
    ingredient = models.ForeignKey(Ingredient,
                                   on_delete=models.CASCADE,
                                   verbose_name='Ингредиенты для рецепта')
    recipe = models.ForeignKey(Recipe,
                               on_delete=models.CASCADE,
                               verbose_name='Рецепт',)
    amount = models.FloatField(
        default=1,
        validators=[MinValueValidator(
            0.01, message='Ингредиента должно быть больше 0.01!')],
        verbose_name='Количество')

    class Meta:
        default_related_name = 'ingredients_in_recipe'
        verbose_name = 'Ингредиент в рецепте'
        verbose_name_plural = 'Ингредиенты в рецепте'
        constraints = [models.UniqueConstraint(
            fields=['recipe', 'ingredient'], name='unique_recipe'
        )]

    def __str__(self):
        return f"{self.recipe}: {self.ingredient} – {self.amount}"


class Favorite(models.Model):
    """
    Модель для избранных рецептов. Связывает модели Recipe и User.
    """

    recipe = models.ForeignKey(
        Recipe,
        related_name='in_favorited',
        on_delete=models.CASCADE,
        verbose_name='Рецепт'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь'
    )

    class Meta:
        ordering = ('user',)
        default_related_name = 'favorite'
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранное'
        constraints = [models.UniqueConstraint(
            fields=['recipe', 'user'], name='unique_favorite')]


class ShoppingCart(models.Model):
    """
    Модель продуктовой корзины
    """

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь'
    )
    date_added = models.DateTimeField(
        verbose_name='Дата добавления', auto_now_add=True, editable=False
    )

    class Meta:
        default_related_name = 'shopping_cart'
        verbose_name = 'Рецепт в списке покупок'
        verbose_name_plural = 'Список покупок'
        constraints = [models.UniqueConstraint(
            fields=['user', 'recipe'], name='unique_shopping_cart'
        )]
