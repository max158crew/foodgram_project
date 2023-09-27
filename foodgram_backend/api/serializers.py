from rest_framework import serializers
from djoser.serializers import UserSerializer
from rest_framework.generics import get_object_or_404
from rest_framework.validators import UniqueTogetherValidator
from rest_framework.exceptions import ValidationError

from recipes.models import Recipe, Ingredient, IngredientRecipe, Tag
from users.models import Follow, User

class TokenSerializer(serializers.Serializer):
    """Сериализатор для получения токена."""
    password = serializers.CharField()
    email = serializers.EmailField()


class UsersSerializer(UserSerializer):
    """
    Сериализатор пользователя с отметкой о подписке
    """

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
        fields = ('id', 'name', 'measure')


class TagSerializer(serializers.ModelSerializer):


    class Meta:
        model = Tag
        fields = (
            'id',
            'name',
            'color',
            'slug',
        )



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

class RecipeShortSerializer(serializers.ModelSerializer):
    """
    Сериализатор короткой карточки рецепта
    """
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class FollowersSerializer(serializers.ModelSerializer):
    """
    Сериализатор получения подписок со списком рецептов авторов
    """
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

    def get_is_subscribed(self, author):
        return Follow.objects.filter(
            user=self.context.get('request').user,
            author=author
        ).exists()

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
    """
    Сериализатор подписки на пользователя
    """

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

