from rest_framework.routers import DefaultRouter
from django.urls import include, path
from django.conf.urls import url

from .views import (RecipeViewSet, IngredientViewSet, TagViewSet)


router = DefaultRouter()

router.register('recipes', RecipeViewSet, basename='recipes')
router.register('ingredients', IngredientViewSet, basename='ingredients')
router.register('tags', TagViewSet, basename='tags')


urlpatterns = [
    #path('recipes/<int:id>/shopping_cart/'),
    #path('recipes/download_shopping_cart/', download_shopping_cart),
    #path('recipes/<int:pk>/ingredients/', FavoriteViewSet.as_view()),
    path('', include('users.urls')),
    path('', include(router.urls)),
]