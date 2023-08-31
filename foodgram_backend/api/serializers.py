from rest_framework import serializers

from recipes.models import Recipe, Ingredient, IngredientRecipe


class IngredientSerializer(serializers.ModelSerializer):


    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measure')



class RecipeSerializer(serializers.ModelSerializer):
    ingredients = IngredientSerializer(many=True, required=False)

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'author', 'text', 'ingredients')


    def create(self, validated_data):
        if 'ingredients' not in self.initial_data:
            recipe = Recipe.objects.create(**validated_data)
            return recipe
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        for ingredient in ingredients:
            current_ingredient, status = Ingredient.objects.get_or_create(**ingredient)
            IngredientRecipe.objects.create(ingredient=current_ingredient, recipe=recipe)
        return recipe

