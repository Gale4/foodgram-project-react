from rest_framework import (filters, generics, mixins, permissions, status,
                            viewsets)
from rest_framework.views import APIView
from recipes.models import Recipe, Tag, Ingredient, Favorite
from djoser.views import UserViewSet
from rest_framework.decorators import api_view, action
from rest_framework.response import Response
from users.models import User, Subscribe
from django.http import JsonResponse
from .serializers import (RecipeSerializer,
                          IngredientSerializer,
                          TagSerializer,
                          CustomUserSerializer, 
                          CustomUserCreateSerializer,
                          RecipeCreateSerializer,
                          FavoriteSerializer,
                          SubscribeSerializer)
from djoser.serializers import SetPasswordSerializer
from django.shortcuts import get_object_or_404


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
    Просмотр и редактирование рецептов,
    добавление в список покупок и избранного.
    """

    queryset = Recipe.objects.all()

    def get_serializer_class(self):
        if self.action == 'create' or self.action == 'partial_update':
            return RecipeCreateSerializer
        return RecipeSerializer
    
    @action(detail=False,
            url_path='download_shopping_cart',
            methods=['post'],
            permission_classes=[permissions.AllowAny])
    def download_shopping_cart(request):
        user = request.user
        serializer = CustomUserSerializer(user)
        return JsonResponse(serializer.data)
    
            
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
    permission_classes = (permissions.AllowAny,)

    def get_serializer_class(self):
        if self.action == 'create':
            return CustomUserCreateSerializer
        if self.action == 'set_password':
            return SetPasswordSerializer
        return CustomUserSerializer
    

    @action(detail=True,
            url_path='subscribe',
            methods=['post', 'delete'],
            permission_classes=[permissions.IsAuthenticatedOrReadOnly])
    def subscribe(self, request, id):
        """Подписка и отписка от автора."""

        author = get_object_or_404(User, id=id)
        serializer = SubscribeSerializer(
            data={'subscriber': request.user.id, 'author': author.id}
        )

        if request.method == 'POST':
            serializer.is_valid(raise_exception=True)
            serializer.save(author=author, subscriber=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED) 
        if request.method == 'DELETE':
            favorite = get_object_or_404(
                Subscribe,
                subscriber=request.user,
                author__id=id
            )
            favorite.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)