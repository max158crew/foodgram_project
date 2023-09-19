from rest_framework import viewsets

from recipes.models import Recipe, User, Tag, Ingredient

from .serializers import RecipeSerializer, UserSerializer, IngredientSerializer, TagSerializer
from .permissions import IsAdminOrAuthorOrReadOnlyPermission



class TagViewSet(viewsets.ModelViewSet):
    """
    Вьюсет тегов
    """
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(viewsets.ModelViewSet):
    """
    Вьюсет ингредиентов
    """
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (IsAdminOrAuthorOrReadOnlyPermission, )
    # filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


