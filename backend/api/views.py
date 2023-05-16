from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.serializers import SetPasswordSerializer
from djoser.views import UserViewSet
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from recipes.models import Favorite, GroceryList, Ingredient, Recipe, Tag
from users.models import Subscribe, User

from api.filters import IngredientSearchFilter, RecipeFilter
from api.permissions import IsAuthorOrReadOnly
from api.serializers import (CustomUserCreateSerializer, CustomUserSerializer,
                             FavoriteSerializer, GrocerySerializer,
                             IngredientSerializer, RecipeCreateSerializer,
                             RecipeSerializer, SubscribeResponseSerializer,
                             SubscribeSerializer, TagSerializer)
from api.utils import download_shopping_cart
from api.pagination import CustomPagination


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Просмотр ингредиентов."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    filter_backends = (IngredientSearchFilter,)
    search_fields = ('^name',)
    lookup_field = 'id'


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Просмотр тегов."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None
    lookup_field = 'id'


class RecipeViewSet(viewsets.ModelViewSet):
    """Работа с рецептами, списоком покупок и избранным."""

    queryset = Recipe.objects.all()
    pagination_class = CustomPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.action == 'create' or self.action == 'partial_update':
            return RecipeCreateSerializer
        return RecipeSerializer

    def get_permissions(self):
        if self.action == ('list', 'retrieve'):
            self.permission_classes = [AllowAny]
        if self.action == ('create', 'shopping_cart',
                           'download_shopping_cart', 'favorite'):
            self.permission_classes = [IsAuthenticated]
        if self.action == ('destroy', 'partial_update'):
            self.permission_classes = [IsAuthorOrReadOnly]
        return [permission() for permission in self.permission_classes]

    @action(detail=True,
            url_path='shopping_cart',
            methods=['post', 'delete'])
    def grocery_list(self, request, pk):
        """Добавление и удаление рецепта в список покупок."""
        recipe = get_object_or_404(Recipe, id=pk)
        serializer = GrocerySerializer(
            data={'user': request.user.id, 'recipe': recipe.id})
        if request.method == 'POST':
            serializer.is_valid(raise_exception=True)
            serializer.save(recipe=recipe, user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            grocery = get_object_or_404(
                GroceryList,
                user=request.user,
                recipe__id=pk)
            grocery.delete()
            return Response('Удален из покупок',
                            status=status.HTTP_204_NO_CONTENT)

    @action(detail=False,
            url_path='download_shopping_cart',
            methods=['get'])
    def download_shopping_cart(self, request):
        """Скачивание списка покупок."""
        return download_shopping_cart(request)

    @action(detail=True,
            url_path='favorite',
            methods=['post', 'delete'])
    def favorite(self, request, pk):
        """Добавление и удаление рецепта из избранного."""
        recipe = get_object_or_404(Recipe, id=pk)
        serializer = FavoriteSerializer(
            data={'user': request.user.id, 'recipe': recipe.id})
        if request.method == 'POST':
            serializer.is_valid(raise_exception=True)
            serializer.save(recipe=recipe, user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            favorite = get_object_or_404(
                Favorite,
                user=request.user,
                recipe__id=pk)
            favorite.delete()
            return Response('Удален из избранного',
                            status=status.HTTP_204_NO_CONTENT)


class CustomUserViewSet(UserViewSet):
    """Работа с пользователетями и подписками."""

    queryset = User.objects.all()
    pagination_class = CustomPagination
    permission_classes = (permissions.AllowAny,)

    def get_serializer_class(self):
        if self.action == 'create':
            return CustomUserCreateSerializer
        if self.action == 'set_password':
            return SetPasswordSerializer
        return CustomUserSerializer

    def get_permissions(self):
        if self.action == ('list', 'create'):
            self.permission_classes = [AllowAny]
        if self.action == ('retrieve', 'me', 'subscribe', 'subscriptions'):
            self.permission_classes = [IsAuthenticated]
        return [permission() for permission in self.permission_classes]

    @action(detail=True,
            url_path='subscribe',
            methods=['post', 'delete'])
    def subscribe(self, request, id=None):
        """Подписка и отписка от автора."""
        author = get_object_or_404(User, id=id)
        serializer = SubscribeSerializer(
            data={'subscriber': request.user.id, 'author': author.id})
        if request.method == 'POST':
            serializer.is_valid(raise_exception=True)
            serializer.save(author=author, subscriber=request.user)
            # Вызов сериализатора для кастомного ответа.
            serializer = SubscribeResponseSerializer(
                author,
                context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            subscribe = get_object_or_404(
                Subscribe,
                subscriber=request.user,
                author__id=id)
            subscribe.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False,
            url_path='subscriptions',
            methods=['get'])
    def subscriptions(self, request):
        """Список пользователей, на которых подписан текущий пользователь."""
        queryset = User.objects.filter(author__subscriber=request.user)
        pages = self.paginate_queryset(queryset)
        serializer = SubscribeResponseSerializer(
            pages,
            many=True,
            context={'request': request})
        return self.get_paginated_response(serializer.data)
