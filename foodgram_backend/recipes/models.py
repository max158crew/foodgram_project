from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Tag(models.Model):
    pass

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

