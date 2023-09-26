from http import HTTPStatus


from django.shortcuts import get_object_or_404
from django.contrib.auth.tokens import default_token_generator
from django.db import IntegrityError
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

from recipes.models import Recipe, Tag, Ingredient
from users.models import Follow, User

from .serializers import RecipeSerializer, UserSerializer, IngredientSerializer, TagSerializer, FollowersSerializer, FollowSerializer, SignUpSerializer
from .permissions import IsAdminOrAuthorOrReadOnlyPermission
from .pagination import RecipePagination


# class UsersViewSet(UserViewSet):
#
#     pagination_class = RecipePagination
#
#     # @action(['GET'], detail=False, permission_classes=[IsAuthenticated])
#     # def me(self, request, *args, **kwargs):
#     #     self.get_object = self.get_instance
#     #     return self.retrieve(request, *args, **kwargs)
#
#     @action(methods=['GET'], detail=False)
#     def subscriptions(self, request):
#         subscriptions_list = self.paginate_queryset(
#             User.objects.filter(following__user=request.user)
#         )
#         serializer = FollowersSerializer(
#             subscriptions_list, many=True, context={
#                 'request': request
#             }
#         )
#         return self.get_paginated_response(serializer.data)
#
#     @action(methods=['POST', 'DELETE'], detail=True)
#     def subscribe(self, request, id):
#         if request.method != 'POST':
#             subscription = get_object_or_404(
#                 Follow,
#                 author=get_object_or_404(User, id=id),
#                 user=request.user
#             )
#             self.perform_destroy(subscription)
#             return Response(status=status.HTTP_204_NO_CONTENT)
#         serializer = FollowSerializer(
#             data={
#                 'user': request.user.id,
#                 'author': get_object_or_404(User, id=id).id
#             },
#             context={'request': request}
#         )
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         return Response(serializer.data, status=status.HTTP_201_CREATED)
@api_view(['POST'])
@permission_classes([AllowAny])
def signup(request):
    serializer = SignUpSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    email = serializer.validated_data['email']
    username = serializer.validated_data['username']
    first_name = serializer.validated_data['first_name']
    last_name = serializer.validated_data['last_name']
    password = serializer.validated_data['password']
    try:
        user, create = User.objects.get_or_create(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            password=password
        )
    except IntegrityError:
        return Response('Email занят', status=HTTPStatus.BAD_REQUEST)

    return Response(serializer.data, status=HTTPStatus.OK)


class TagViewSet(viewsets.ModelViewSet):

    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(viewsets.ModelViewSet):

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (IsAdminOrAuthorOrReadOnlyPermission, )
    # filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer




