from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import RecipeViewSet, UserViewSet, TagViewSet, IngredientViewSet, ShowSubscriptionsView, SubscribeView

router = DefaultRouter()
router.register('recipes', RecipeViewSet)
router.register('users', UserViewSet)
router.register('ingredients', IngredientViewSet)
router.register('tags', TagViewSet)


urlpatterns = (
    path('users/subscriptions/', ShowSubscriptionsView.as_view()),
    path('users/suscribe', SubscribeView),
    path('', include(router.urls)),
    path('auth/', include('djoser.urls.authtoken')),
)


