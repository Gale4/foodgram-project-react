from rest_framework import serializers
from recipes.models import Recipe, Ingredient
from users.models import User
from djoser.serializers import UserSerializer, UserCreateSerializer

class RecipeSerializer(serializers.ModelSerializer):
    """Отображение рецепта."""

    class Meta:
        model = Recipe
        fields = ('__all__',)

class IngredientSerializer(serializers.ModelSerializer):
    """Отображение ингридиента."""

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')

class CustomUserSerializer(UserSerializer):
    """Работа с пользователем."""

    class Meta(UserSerializer.Meta):
        fields = ('email', 'id', 'username', 'first_name', 'last_name')

class CustomUserCreateSerializer(UserCreateSerializer):
    """Регистрация."""
    password = serializers.CharField(write_only=True)

    class Meta(UserCreateSerializer.Meta):
        fields = ('email', 'username', 'first_name', 'last_name', 'password')