import base64

from django.db import transaction
from django.core.files.base import ContentFile
from djoser.serializers import UserCreateSerializer, UserSerializer
from django.shortcuts import get_object_or_404
from rest_framework import serializers

from foodgram.settings import DEFAULT_RECIPE_LIMIT
from recipes.models import (Favorite, GroceryList, Ingredient, Recipe,
                            RecipeIngredients, Tag)
from users.models import Subscribe, User


class Base64ImageField(serializers.ImageField):
    """Кодирорование и декодирование изображения Base64."""

    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


class CustomUserSerializer(UserSerializer):
    """Работа с пользователем."""

    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta(UserSerializer.Meta):
        fields = ('email', 'id', 'username',
                  'first_name', 'last_name', 'is_subscribed')

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if user is None or user.is_anonymous:
            return False
        return obj.author.filter(subscriber=user, author=obj).exists()


class CustomUserCreateSerializer(UserCreateSerializer):
    """Регистрация."""

    password = serializers.CharField(write_only=True)

    class Meta(UserCreateSerializer.Meta):
        fields = ('email', 'username', 'first_name', 'last_name', 'password')


class TagSerializer(serializers.ModelSerializer):
    """Отображение тегов."""

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    """Отображение ингридиента."""

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class IngredientAmountSerializer(serializers.ModelSerializer):
    """Добавление ингредиента в рецепт."""

    id = serializers.IntegerField()
    amount = serializers.IntegerField()

    class Meta:
        model = RecipeIngredients
        fields = ('id', 'amount')

    def validate_amount(self, value):
        if value < 1:
            raise serializers.ValidationError('Меньше минимального.')
        return value


class IngredientsRecipeSerializer(serializers.ModelSerializer):
    """Отображение ингредиентов в рецепте."""

    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit')

    class Meta:
        model = RecipeIngredients
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    """Отображение рецепта."""

    ingredients = IngredientsRecipeSerializer(
        many=True,
        source='ingredients_in')
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    author = CustomUserSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients', 'is_favorited',
                  'is_in_shopping_cart', 'name', 'image',
                  'text', 'cooking_time')

    def get_is_favorited(self, obj):
        user = self.context.get('request').user
        if user is None or user.is_anonymous:
            return False
        return obj.favorite.filter(user=user, recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        if user is None or user.is_anonymous:
            return False
        return obj.in_grocery_list.filter(user=user, recipe=obj).exists()


class RecipeCreateSerializer(serializers.ModelSerializer):
    """Добавление и редактирование рецепта."""

    ingredients = IngredientAmountSerializer(
        many=True,
        partial=True)
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all())
    image = Base64ImageField(required=True)

    class Meta:
        model = Recipe
        fields = ('ingredients', 'tags', 'image',
                  'name', 'text', 'cooking_time')

    def to_representation(self, instance):
        serializer = RecipeSerializer(
            instance,
            context={'request': self.context.get('request')})
        return serializer.data

    def add_ingredient(self, ingredients, recipe):
        """Добавление ингридиета при создании и изменении рецепта."""
        RecipeIngredients.objects.bulk_create([
            RecipeIngredients(
                recipe=recipe,
                amount=ingredient['amount'],
                ingredient=get_object_or_404(
                    Ingredient,
                    id=ingredient['id']),
            ) for ingredient in ingredients])

    @transaction.atomic
    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        user = self.context.get('request').user
        recipe = Recipe.objects.create(author=user, **validated_data)
        recipe.tags.set(tags)
        self.add_ingredient(ingredients, recipe)
        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        instance.tags.clear()
        instance.tags.set(tags)
        instance.ingredients.clear()
        self.add_ingredient(ingredients, instance)
        instance.save()
        return super().update(instance, validated_data)


class RecipeDataSerializer(serializers.ModelSerializer):
    """Сериализатор коротких данных рецепта."""

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class GrocerySerializer(serializers.ModelSerializer):
    """Работа со списком покупок."""

    user = serializers.IntegerField(source='user.id', write_only=True)
    recipe = serializers.IntegerField(source='recipe.id', write_only=True)

    class Meta:
        model = GroceryList
        fields = ('id', 'user', 'recipe')

    def validate(self, data):
        user = data['user']['id']
        recipe = data['recipe']['id']
        if GroceryList.objects.filter(user__id=user,
                                      recipe__id=recipe).exists():
            raise serializers.ValidationError({'errors': 'Уже в списке.'})
        return data

    def to_representation(self, instance):
        serializer = RecipeDataSerializer(
            instance.recipe,
            context={'request': self.context.get('request')})
        return serializer.data


class FavoriteSerializer(serializers.ModelSerializer):
    """Добавление и удаление рецепта из избранного."""

    user = serializers.IntegerField(source='user.id', write_only=True)
    recipe = serializers.IntegerField(source='recipe.id', write_only=True)

    class Meta:
        model = Favorite
        fields = ('id', 'user', 'recipe')

    def validate(self, data):
        user = data['user']['id']
        recipe = data['recipe']['id']
        if Favorite.objects.filter(user__id=user, recipe__id=recipe).exists():
            raise serializers.ValidationError({'errors': 'Уже в избранном.'})
        return data

    def create(self, validated_data):
        user = validated_data['user']
        recipe = validated_data['recipe']
        Favorite.objects.get_or_create(user=user, recipe=recipe)
        return validated_data

    def to_representation(self, instance):
        serializer = RecipeDataSerializer(
            instance['recipe'],
            context={'request': self.context.get('request')})
        return serializer.data


class SubscribeSerializer(serializers.ModelSerializer):
    """Сериализатор подписки и отписки."""

    subscriber = serializers.IntegerField(
        source='subscriber.id',
        write_only=True)
    author = serializers.IntegerField(
        source='author.id',
        write_only=True)

    class Meta:
        model = Subscribe
        fields = ('id', 'subscriber', 'author')

    def validate(self, data):
        subscriber = data['subscriber']['id']
        author = data['author']['id']
        if Subscribe.objects.filter(
            subscriber__id=subscriber,
            author__id=author,
        ).exists():
            raise serializers.ValidationError(
                {'errors': 'Вы уже подписаны на этого автора.'})
        if subscriber == author:
            raise serializers.ValidationError(
                {'errors': 'Нельзя подписаться на себя.'})
        return data

    def create(self, validated_data):
        subscriber = validated_data['subscriber']
        author = validated_data['author']
        Subscribe.objects.get_or_create(subscriber=subscriber, author=author)
        return validated_data


class SubscribeResponseSerializer(serializers.ModelSerializer):
    """Список подписок пользователя и ответных данных на подписку."""

    is_subscribed = serializers.BooleanField(default=True)
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'is_subscribed', 'recipes', 'recipes_count')

    def get_recipes(self, obj):
        """Отображение рецептов автора в подписках."""
        queryset = self.context.get('request')
        recipes_limit = queryset.query_params.get(
            'recipes_limit',
            DEFAULT_RECIPE_LIMIT)
        return RecipeDataSerializer(
            obj.recipes.all()[:int(recipes_limit)],
            many=True).data

    def get_recipes_count(self, obj):
        """Счётчик рецептов."""
        return obj.recipes.filter(author=obj).count()
