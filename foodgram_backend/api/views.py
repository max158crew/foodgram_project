from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.permissions import (SAFE_METHODS, IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import filters, status
from djoser.views import UserViewSet

from recipes.models import Recipe, Tag, Ingredient
from users.models import Follow, User

from .serializers import RecipeSerializer, UserSerializer, IngredientSerializer, TagSerializer, FollowersSerializer, FollowSerializer
from .permissions import IsAdminOrAuthorOrReadOnlyPermission
from .pagination import RecipePagination


class UsersViewSet(UserViewSet):

    pagination_class = RecipePagination

    @action(['GET'], detail=False, permission_classes=[IsAuthenticated])
    def me(self, request, *args, **kwargs):
        self.get_object = self.get_instance
        return self.retrieve(request, *args, **kwargs)

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


