from rest_framework import (filters, generics, mixins, permissions, status,
                            viewsets)
from rest_framework.views import APIView
from recipes.models import Recipe, Tag, Ingredient
from djoser.views import UserViewSet
from rest_framework.decorators import api_view
from rest_framework.response import Response
from users.models import User
from django.http import JsonResponse
from .serializers import (RecipeSerializer,
                          IngredientSerializer,
                          TagSerializer,
                          CustomUserSerializer, 
                          CustomUserCreateSerializer,
                          RecipeCreateSerializer)
from djoser.serializers import SetPasswordSerializer
from django.shortcuts import get_object_or_404



class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    
    def get_serializer_class(self):
        if self.action == 'create' or self.action == 'partial_update':
            return RecipeCreateSerializer
        return RecipeSerializer

    def perform_create(self, serializer):
        serializer.is_valid(raise_exception=True)
        serializer.save(author=self.request.user)

'''
    @api_view(['PATCH',])
    def patch(request, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        serializer = RecipeEditSerializer(recipe, data=request.data, partial=True)
        #потом поменять на serializer.is_valid(raise_exception=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_405_METHOD_NOT_ALLOWED)'''
'''
class RecipeViewSet(viewsets.ViewSet):
    def list(self, request):
        queryset = Recipe.objects.all()
        serializer = RecipeSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        queryset = Recipe.objects.all()
        recipe = get_object_or_404(queryset, pk=pk)
        serializer = RecipeSerializer(recipe)
        return Response(serializer.data)
    
    def create(self, request):
        queryset = Recipe.objects.all()
        serializer = RecipeCreateSerializer(queryset, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(author=self.request.user)
  '''    


class FavoriteDetail(APIView):
    def post(self, request, pk):
        pass
    def delete(self, request, pk):
        pass

class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Просмотр ингредиентов."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Просмотр тегов."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer


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


@api_view(['GET',])
def download_shopping_cart(request):
      user = request.user
      serializer = CustomUserSerializer(user)
      return JsonResponse(serializer.data)
