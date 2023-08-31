from django.db import models

class Tag(models.Model):
    pass

class Ingredient(models.Model):
    name = models.CharField(max_length=128)
    measure = models.CharField(max_length=64)

    def __str__(self):
        return self.name

class Recipe(models.Model):
    name = models.CharField(max_length=128)
    author = models.CharField(max_length=16)
    text = models.TextField()
    ingredients = models.ManyToManyField(Ingredient, through='IngredientRecipe')

    def __str__(self):
        return self.name

class IngredientRecipe(models.Model):
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)

class Cart(models.Model):
    pass

class Favorite(models.Model):
    pass

