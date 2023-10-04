from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import RecipeViewSet, UserViewSet, TagViewSet, IngredientViewSet

router = DefaultRouter()
router.register('recipes', RecipeViewSet)
router.register('users', UserViewSet)
router.register('ingredients', IngredientViewSet)
router.register('tags', TagViewSet)


urlpatterns = (
    path('', include(router.urls)),
    path('auth/', include('djoser.urls.authtoken')),
)


