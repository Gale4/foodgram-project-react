from rest_framework import serializers
from recipes.models import Recipe


class RecipeSerializer(serializers.ModelSerializer):
    """Отображение рецепта."""

    class Meta:
        model = Recipe
        fields = ('__all__',)
