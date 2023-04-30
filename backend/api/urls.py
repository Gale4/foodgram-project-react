from rest_framework.routers import DefaultRouter
from django.urls import include, path
from django.conf.urls import url

from .views import RecipeViewSet, IngredientViewSet


router = DefaultRouter()

router.register('recipes', RecipeViewSet, basename='recipes')
router.register('ingredients', IngredientViewSet, basename='ingredients')


urlpatterns = [
    url(r'^', include('users.urls')),
    path('', include(router.urls)),
]