from rest_framework import (filters, generics, mixins, permissions, status,
                            viewsets)
from rest_framework.views import APIView
from recipes.models import Recipe, Tag, Ingredient
from djoser.views import UserViewSet
from rest_framework.decorators import api_view, action
from rest_framework.response import Response
from users.models import User
from django.http import JsonResponse
from .serializers import (RecipeSerializer,
                          IngredientSerializer,
                          TagSerializer,
                          CustomUserSerializer, 
                          CustomUserCreateSerializer,
                          RecipeCreateSerializer,
                          FavoriteSerializer)
from djoser.serializers import SetPasswordSerializer
from django.shortcuts import get_object_or_404


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Просмотр ингредиентов."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Просмотр тегов."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    """Просмотр и редактирование рецептов."""

    queryset = Recipe.objects.all()

    def get_serializer_class(self):
        if self.action == 'create' or self.action == 'partial_update':
            return RecipeCreateSerializer
        return RecipeSerializer
    
    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
    
    def perform_update(self, serializer):
        serializer.save(author=self.request.user)
    
    @action(detail=False,
            url_path='download_shopping_cart',
            methods=['post'],
            permission_classes=[permissions.AllowAny])
    def download_shopping_cart(request):
        user = request.user
        serializer = CustomUserSerializer(user)
        return JsonResponse(serializer.data)


class CustomUserViewSet(UserViewSet):
    """Работа с пользователетями."""

    queryset = User.objects.all()
    permission_classes = (permissions.AllowAny,)

    def get_serializer_class(self):
        if self.action == 'create':
            return CustomUserCreateSerializer
        if self.action == 'set_password':
            return SetPasswordSerializer
        return CustomUserSerializer


class FavoriteViewSet(mixins.CreateModelMixin,
                      mixins.DestroyModelMixin,
                      viewsets.GenericViewSet):
    """Работа с избранным."""

    serializer_class = FavoriteSerializer

