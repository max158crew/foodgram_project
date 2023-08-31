from django.db import models


class Recipe(models.Model):
    name = models.CharField(max_length=128)
    author = models.CharField(max_length=16)
    text = models.TextField()

