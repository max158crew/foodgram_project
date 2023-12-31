from django.db import transaction
from rest_framework import serializers
from djoser.serializers import UserSerializer
from rest_framework.generics import get_object_or_404
from rest_framework.validators import UniqueTogetherValidator
from rest_framework.exceptions import ValidationError

from recipes.models import (Recipe, Ingredient, IngredientRecipe, Tag,
                            Favorite, ShoppingCart)
from users.models import Follow, User
from .fields import Base64ImageField


class UsersSerializer(UserSerializer):

    is_subscribed = serializers.SerializerMethodField()

    def get_is_subscribed(self, obj: User):
        request = self.context.get("request")
        if not request or request.user.is_anonymous:
            return False
        return Follow.objects.filter(user=request.user, author=obj).exists()

    class Meta:
        model = User
        fields = ("email",
                  "id",
                  "username",
                  "first_name",
                  "last_name",
                  "is_subscribed"
                  )


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = (
            'id',
            'name',
            'color',
            'slug',
        )


class RecipeShortSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class GetIngredientsInRecipeSerializer(serializers.ModelSerializer):

    id = serializers.PrimaryKeyRelatedField(
        source="ingredient", read_only=True)
    name = serializers.SlugRelatedField(
        source="ingredient", read_only=True, slug_field="name")
    measurement_unit = serializers.SlugRelatedField(
        source="ingredient", read_only=True, slug_field="measurement_unit")

    class Meta:
        model = IngredientRecipe
        fields = (
            "id",
            "name",
            "measurement_unit",
            "amount",
        )


class GetRecipeSerializer(serializers.ModelSerializer):

    image = Base64ImageField(required=False, allow_null=True)
    tags = TagSerializer(many=True, read_only=True)
    ingredients = GetIngredientsInRecipeSerializer(
        many=True,
        read_only=True,
        source="ingredients_in_recipe",
    )
    author = UsersSerializer(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)
    is_favorited = serializers.SerializerMethodField(read_only=True)

    def get_is_favorited(self, obj):
        request = self.context.get("request")
        if request.user.is_anonymous:
            return False
        return Favorite.objects.filter(
            user=request.user, recipe__id=obj.id).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get("request")
        if request.user.is_anonymous:
            return False
        return ShoppingCart.objects.filter(
            user=request.user, recipe__id=obj.id).exists()

    class Meta:
        model = Recipe
        fields = (
            "id",
            "tags",
            "author",
            "ingredients",
            "is_favorited",
            "is_in_shopping_cart",
            "name",
            "image",
            "text",
            "cooking_time",
        )


class CreateIngredientsInRecipeSerializer(serializers.ModelSerializer):

    id = serializers.PrimaryKeyRelatedField(
        source="ingredient", queryset=Ingredient.objects.all())
    amount = serializers.FloatField()

    def validate_amount(self, data):
        """ Проверка введенного количества ингредиента."""
        try:
            quantity = float(data)
            if quantity < 0.001:
                raise serializers.ValidationError(
                    "Ингредиента должно быть не менее 0.001."
                )
        except ValueError:
            raise serializers.ValidationError("Неверный вес")
        return data

    def create(self, validated_data):

        return IngredientRecipe.objects.create(
            ingredient=validated_data.get("id"),
            amount=validated_data.get("amount")
        )

    class Meta:
        model = IngredientRecipe
        fields = (
            "id",
            "amount",
        )


class CreateRecipeSerializer(serializers.ModelSerializer):

    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True, required=True)
    image = Base64ImageField(use_url=True, max_length=None)
    author = UserSerializer(read_only=True)
    ingredients = CreateIngredientsInRecipeSerializer(many=True, required=True)
    cooking_time = serializers.IntegerField()

    def __create_ingredients(self, recipe, ingredients):
        IngredientRecipe.objects.bulk_create([
            IngredientRecipe(
                recipe=recipe,
                amount=ingredient['amount'],
                ingredient=ingredient['ingredient'],
            ) for ingredient in ingredients
        ])

    def validate(self, data):
        ingredients = data.get('ingredients')
        tags_ids = data.get('tags')
        if not tags_ids or not ingredients:
            raise ValidationError("Недостаточно данных.")
        ingredients_list = []
        for ingredient in ingredients:
            if ingredient in ingredients_list:
                raise ValidationError(
                    "Есть задублированные ингредиенты!"
                )
            ingredients_list.append(ingredient)

        tags_list = []
        for tag in tags_ids:
            if tag in tags_list:
                raise ValidationError(
                    "Есть задублированные тэги!"
                )
            tags_list.append(tag)

        if data['cooking_time'] < 1:
            raise ValidationError(
                "Время приготовления должно быть не менее 1 минуты!"
            )
        return data

    @transaction.atomic
    def create(self, validated_data):
        request = self.context.get('request')
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(
            author=request.user,
            **validated_data
        )
        self.__create_ingredients(recipe, ingredients)
        recipe.tags.set(tags)
        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients')
        IngredientRecipe.objects.filter(recipe=instance).delete()
        self.__create_ingredients(instance, ingredients)
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        return GetRecipeSerializer(
            instance,
            context={
                'request': self.context.get('request'),
            }
        ).data

    class Meta:
        model = Recipe
        fields = (
            'id',
            'author',
            'ingredients',
            'tags',
            'image',
            'name',
            'text',
            'cooking_time',
        )


class FollowersSerializer(UsersSerializer):

    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    def get_recipes_count(self, author):
        return Recipe.objects.filter(author=author).count()

    def get_recipes(self, author):
        queryset = self.context.get('request')
        recipes_limit = queryset.query_params.get('recipes_limit')
        if not recipes_limit:
            return RecipeShortSerializer(
                Recipe.objects.filter(author=author),
                many=True, context={'request': queryset}
            ).data
        return RecipeShortSerializer(
            Recipe.objects.filter(author=author)[:int(recipes_limit)],
            many=True,
            context={'request': queryset}
        ).data

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count'
        )


class FollowSerializer(serializers.ModelSerializer):

    def validate(self, data):
        get_object_or_404(User, username=data['author'])
        if self.context['request'].user == data['author']:
            raise ValidationError({
                'Нельзя подписаться на себя'
            })
        return data

    def to_representation(self, instance):
        return FollowersSerializer(
            instance.author,
            context={'request': self.context.get('request')}
        ).data

    class Meta:
        model = Follow
        fields = ('user', 'author')
        validators = [
            UniqueTogetherValidator(
                queryset=Follow.objects.all(),
                fields=('user', 'author'),
                message='Вы уже подписаны'
            )
        ]


class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorite
        fields = (
            'id',
            'user',
            'recipe',
        )
        validators = [UniqueTogetherValidator(
            queryset=Favorite.objects.all(),
            fields=('user', 'recipe'),
            message='Рецепт уже в избранном')]

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return RecipeShortSerializer(
            instance.recipe, context=context).data


class ShoppingCartSerializer(serializers.ModelSerializer):

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return RecipeShortSerializer(instance.recipe, context=context).data

    class Meta:
        model = ShoppingCart
        fields = (
            'id',
            'user',
            'recipe',
        )
        validators = [UniqueTogetherValidator(
            queryset=ShoppingCart.objects.all(),
            fields=('user', 'recipe'),
            message='Рецепт уже в корзине')
        ]
