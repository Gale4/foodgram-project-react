from rest_framework import viewsets
from recipes.models import Recipe, Tag, Ingredient
from djoser.views import UserViewSet
from users.models import User
from .serializers import (RecipeSerializer,
                          IngredientSerializer, 
                          CustomUserSerializer, 
                          CustomUserCreateSerializer)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer

class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    
class CustomUserViewSet(UserViewSet):

    def get_serializer_class(self):
        if self.request.method in ['POST', 'PUT', 'PATCH']:
            return CustomUserCreateSerializer
        return CustomUserSerializer
      
    def get_queryset(self):
        return User.objects.all()