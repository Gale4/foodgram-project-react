from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from djoser.serializers import SetPasswordSerializer
from djoser.views import UserViewSet
from rest_framework import (filters, generics, mixins, permissions, status,
                            viewsets)
from rest_framework.decorators import action, api_view
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from recipes.models import Favorite, Ingredient, Recipe, Tag, GroceryList
from users.models import Subscribe, User
from .utils import download_shopping_cart

from .serializers import (CustomUserCreateSerializer, CustomUserSerializer,
                          FavoriteSerializer, IngredientSerializer,
                          RecipeCreateSerializer, RecipeSerializer,
                          SubscribeResponseSerializer, SubscribeSerializer,
                          TagSerializer, GrocerySerializer)


class CreateDestroyViewSet(mixins.CreateModelMixin,
                           mixins.DestroyModelMixin,
                           viewsets.GenericViewSet):
    """Кастомный вьюсет для создания и удаления экземпляров."""


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Просмотр ингредиентов."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Просмотр тегов."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    """
    Просмотр и редактирование рецептов
    добавление в список покупок и избранного.
    """

    queryset = Recipe.objects.all()

    def get_serializer_class(self):
        if self.action == 'create' or self.action == 'partial_update':
            return RecipeCreateSerializer
        return RecipeSerializer

    @action(detail=True,
            url_path='shopping_cart',
            methods=['post', 'delete'])
    def grocery_list(self, request, pk):
        """Добавление и удаление рецепта в список покупок."""
        recipe = get_object_or_404(Recipe, id=pk)
        serializer = GrocerySerializer(
            data={'user': request.user.id, 'recipe': recipe.id}
        )
        if request.method == 'POST':
            serializer.is_valid(raise_exception=True)
            serializer.save(recipe=recipe, user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            grocery = get_object_or_404(
                GroceryList,
                user=request.user,
                recipe__id=pk
            )
            grocery.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False,
            url_path='download_shopping_cart',
            methods=['get'],
            permission_classes=[permissions.IsAuthenticated])
    def download_shopping_cart(self, request):
        """Скачивание списка покупок."""
        return download_shopping_cart(request)

    @action(detail=True,
            url_path='favorite',
            methods=['post', 'delete'],
            permission_classes=[permissions.IsAuthenticatedOrReadOnly])
    def favorite(self, request, pk):
        """Добавление и удаление рецепта из избранного."""
        recipe = get_object_or_404(Recipe, id=pk)
        serializer = FavoriteSerializer(
            data={'user': request.user.id, 'recipe': recipe.id}
        )

        if request.method == 'POST':
            serializer.is_valid(raise_exception=True)
            serializer.save(recipe=recipe, user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            favorite = get_object_or_404(
                Favorite,
                user=request.user,
                recipe__id=pk
            )
            favorite.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)


class CustomUserViewSet(UserViewSet):
    """Работа с пользователетями."""

    queryset = User.objects.all()
    pagination_class = PageNumberPagination
    permission_classes = (permissions.AllowAny,)

    def get_serializer_class(self):
        if self.action == 'create':
            return CustomUserCreateSerializer
        if self.action == 'set_password':
            return SetPasswordSerializer
        return CustomUserSerializer
    
    '''def get_permissions(self):
    """
    Instantiates and returns the list of permissions that this view requires.
    """
    if self.action == 'list':
        permission_classes = [IsAuthenticated]'''
    
    @action(detail=True,
            url_path='subscribe',
            methods=['post', 'delete'],
            permission_classes=[permissions.IsAuthenticated])
    def subscribe(self, request, id=None):
        """Подписка и отписка от автора."""
        author = get_object_or_404(User, id=id)
        serializer = SubscribeSerializer(
            data={'subscriber': request.user.id, 'author': author.id}
        )

        if request.method == 'POST':
            serializer.is_valid(raise_exception=True)
            serializer.save(author=author, subscriber=request.user)
            # Вызов сериализатора для кастомного ответа.
            serializer = SubscribeResponseSerializer(
                author,
                context={'request': request}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            subscribe = get_object_or_404(
                    Subscribe,
                    subscriber=request.user,
                    author__id=id
                )
            subscribe.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False,
            url_path='subscriptions',
            methods=['get'],
            permission_classes=[permissions.IsAuthenticated])
    def subscriptions(self, request):
        """
        Возвращает пользователей,
        на которых подписан текущий пользователь.
        """
        queryset = User.objects.filter(author__subscriber=request.user)
        pages = self.paginate_queryset(queryset)
        serializer = SubscribeResponseSerializer(
            pages,
            many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)
