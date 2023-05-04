from rest_framework import serializers
from recipes.models import Tag, Recipe, Ingredient, RecipeIngredients, GroceryList, Favorite
from users.models import User, Subscribe
from djoser.serializers import UserSerializer, UserCreateSerializer
import base64
from django.core.files.base import ContentFile



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
        fields = ('email', 'id', 'username', 'first_name', 'last_name', 'is_subscribed')

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return Subscribe.objects.filter(subscriber=request.user, author=obj).exists()


class CustomUserCreateSerializer(UserCreateSerializer):
    """Регистрация."""

    password = serializers.CharField(write_only=True)

    class Meta(UserCreateSerializer.Meta):
        fields = ('email', 'username', 'first_name', 'last_name', 'password')



class IngredientSerializer(serializers.ModelSerializer):
    """Отображение ингридиента."""

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class IngredientAmountInteractSerializer(serializers.ModelSerializer):
    """Отображение ингредиента в рецепте."""

    #id = serializers.IntegerField()
    amount = serializers.IntegerField(write_only=True, )

    def validate_amount(self, value):
        if value < 1:
            raise serializers.ValidationError('Меньше минимального.')
        return value

    class Meta:
        model = RecipeIngredients
        fields = ('id', 'amount')


class TagSerializer(serializers.ModelSerializer):
    """Отображение тегов."""

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')

class RecipeSerializer(serializers.ModelSerializer):
    """Отображение рецепта."""

    ingredients = IngredientAmountInteractSerializer(many=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    author = CustomUserSerializer(read_only=True)
    #tags = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all(), many=True)


    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return Favorite.objects.filter(user=request.user, recipe=obj).exists()
    
    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return GroceryList.objects.filter(user=request.user, recipe=obj).exists()

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients', 'is_favorited',
                  'is_in_shopping_cart', 'name', 'image',
                  'text', 'cooking_time')
        

class RecipeCreateSerializer(serializers.ModelSerializer):
    """Добавление рецепта."""

    ingredients = IngredientAmountInteractSerializer(many=True)
    image = Base64ImageField(required=True)
    image = Base64ImageField(required=True)


    class Meta:
        model = Recipe
        fields = ('ingredients', 'tags', 'image', 'name', 'text', 'cooking_time')


    def validate_cooking_time(self, value):
        if value < 1:
            raise serializers.ValidationError('Неправильное время готовки.')
        return value
    
    def create(self, validated_data):
        request = self.context.get('request')
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)

        for ingredient in ingredients:
            current_ingredient, status = Ingredient.objects.get_or_create(
                **ingredient)
        RecipeIngredients.objects.create(
                ingredient=current_ingredient, recipe=recipe)
        return recipe