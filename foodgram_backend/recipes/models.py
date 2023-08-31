from django.db import models

class Tag(models.Model):
    pass

class Ingridient(models.Model):
    pass

class Recipe(models.Model):
    name = models.CharField(max_length=128)
    author = models.CharField(max_length=16)
    text = models.TextField()

class IngridientRecipe(models.Model):
    pass

class Cart(models.Model):
    pass

class Favorite(models.Model):
    pass

