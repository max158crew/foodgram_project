from http import HTTPStatus


from django.shortcuts import get_object_or_404
from django.contrib.auth.tokens import default_token_generator
from django.db import IntegrityError
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
)
from rest_framework.permissions import (SAFE_METHODS, IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework import filters, status
from djoser.views import UserViewSet
from rest_framework_simplejwt.tokens import AccessToken

from recipes.models import Recipe, Tag, Ingredient, ShoppingCart, Favorite
from users.models import Follow, User

from .serializers import IngredientSerializer, TagSerializer, \
    FollowersSerializer, FollowSerializer,\
    TokenSerializer, GetRecipeSerializer, CreateRecipeSerializer, \
    ShoppingCartSerializer, FavoriteSerializer
from .permissions import IsAdminOrAuthorOrReadOnlyPermission
from .pagination import RecipePagination
from .filters import RecipeFilter
from .utility import download_shopping_list


@api_view(['POST'])
@permission_classes([AllowAny])
def token_jwt(request):
    serializer = TokenSerializer(data=request.data)
    if serializer.is_valid():
        user = get_object_or_404(
            User, email=request.data.get('email')
        )
        token = {'auth_token': str(AccessToken.for_user(user))}
        return Response(token, status=HTTPStatus.OK)
    return Response(serializer.errors, status=HTTPStatus.BAD_REQUEST)


class UsersViewSet(UserViewSet):

    pagination_class = RecipePagination


    @action(methods=['GET'], detail=False)
    def subscriptions(self, request):
        subscriptions_list = self.paginate_queryset(
            User.objects.filter(following__user=request.user)
        )
        serializer = FollowersSerializer(
            subscriptions_list, many=True, context={
                'request': request
            }
        )
        return self.get_paginated_response(serializer.data)

    @action(methods=['POST', 'DELETE'], detail=True)
    def subscribe(self, request, id):
        if request.method != 'POST':
            subscription = get_object_or_404(
                Follow,
                author=get_object_or_404(User, id=id),
                user=request.user
            )
            self.perform_destroy(subscription)
            return Response(status=status.HTTP_204_NO_CONTENT)
        serializer = FollowSerializer(
            data={
                'user': request.user.id,
                'author': get_object_or_404(User, id=id).id
            },
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)



class TagViewSet(viewsets.ModelViewSet):

    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(viewsets.ModelViewSet):

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (IsAdminOrAuthorOrReadOnlyPermission, )
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)



class RecipeViewSet(viewsets.ModelViewSet):


    queryset = Recipe.objects.all()
    serializer_class = GetRecipeSerializer
    pagination_class = RecipePagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    permission_classes = (
        IsAdminOrAuthorOrReadOnlyPermission, IsAuthenticatedOrReadOnly
    )

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return GetRecipeSerializer
        return CreateRecipeSerializer

    @staticmethod
    def __post_method_for_actions(request, pk, serializers):
        data = {'user': request.user.id, 'recipe': pk}
        serializer = serializers(data=data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @staticmethod
    def __delete_method_for_actions(request, pk, model):
        recipe = get_object_or_404(Recipe, id=pk)
        model_instance = get_object_or_404(
            model, user=request.user, recipe=recipe)
        model_instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['POST'])
    def shopping_cart(self, request, pk):
        return self.__post_method_for_actions(
            request, pk, serializers=ShoppingCartSerializer
        )

    @shopping_cart.mapping.delete
    def delete_shopping_cart(self, request, pk):
        return self.__delete_method_for_actions(
            request=request, pk=pk, model=ShoppingCart)

    @action(
        detail=False, methods=['GET'], permission_classes=(IsAuthenticated,)
    )
    def download_shopping_cart(self, request):
        return download_shopping_list(request)

    @action(detail=True, methods=['POST'])
    def favorite(self, request, pk):
        return self.__post_method_for_actions(
            request=request, pk=pk, serializers=FavoriteSerializer)

    @favorite.mapping.delete
    def delete_favorite(self, request, pk):
        return self.__delete_method_for_actions(
            request=request, pk=pk, model=Favorite)





