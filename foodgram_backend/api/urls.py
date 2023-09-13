from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import RecipeViewSet, UserViewSet, TagViewSet, IngredientViewSet

router = DefaultRouter()
router.register(r'recipes', RecipeViewSet)
router.register(r'users', UserViewSet)
router.register('ingredients', IngredientViewSet)
router.register('tags', TagViewSet)


urlpatterns = (
    path('', include(router.urls)),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.jwt')),
)
