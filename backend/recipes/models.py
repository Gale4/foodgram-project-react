from colorfield.fields import ColorField
from django.db import models
from django.core.validators import MinValueValidator

from users.models import User


class Tag(models.Model):
    """Модель тега."""

    name = models.CharField(
        max_length=200,
        unique=True,
        verbose_name='Имя тэга')
    color = ColorField(
        unique=True,
        verbose_name='Цвет')
    slug = models.SlugField(unique=True)

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        constraints = (
            models.UniqueConstraint(
                fields=('name', 'color', 'slug'),
                name='unique_tags',
            ),
        )

    def __str__(self) -> str:
        return self.name


class Ingredient(models.Model):
    """Модель ингредиента."""

    name = models.CharField(
        max_length=200,
        verbose_name='Название ингредиента')
    measurement_unit = models.CharField(
        max_length=200,
        verbose_name='Единица измерения')

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ['name']
        constraints = (
            models.UniqueConstraint(
                fields=('name', 'measurement_unit'),
                name='unique_ingredients',
            ),
        )

    def __str__(self) -> str:
        return self.name


class Recipe(models.Model):
    """Модель рецепта."""

    name = models.CharField(
        max_length=200,
        verbose_name='Название')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор')
    text = models.TextField(
        blank=False,
        verbose_name='Описание рецепта')
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredients',
        related_name='recipe',
        verbose_name='Ингредиенты')
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Тэги')
    image = models.ImageField(
        upload_to='recipes/images/',
        null=False,
        default=None,
        verbose_name='Фото')
    cooking_time = models.PositiveSmallIntegerField(
        default=1,
        blank=False,
        validators=[MinValueValidator(1, 'не может быть < 1')],
        verbose_name='Время приготовления')
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата рецепта')

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ['-pub_date']

    def __str__(self) -> str:
        return self.name


class RecipeIngredients(models.Model):
    """Связь ингредиента с рецептом."""

    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='in_recipe')
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='ingredients_in')
    amount = models.IntegerField(
        default=1,
        validators=[MinValueValidator(1, 'не может быть < 1')])

    class Meta:
        default_related_name = 'recipe_ingridients'

    def __str__(self) -> str:
        return f'{self.recipe} {self.ingredient} {self.amount}'


class GroceryList(models.Model):
    """Модель списка покупок."""

    user = models.ForeignKey(
        User,
        related_name='in_grocery_list',
        on_delete=models.CASCADE,
        verbose_name='Пользователь')
    recipe = models.ForeignKey(
        Recipe,
        related_name='in_grocery_list',
        on_delete=models.CASCADE,
        verbose_name='Рецепт в корзине')

    class Meta:
        verbose_name_plural = 'Корзина покупок'
        default_related_name = 'grocery_list'
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique_recipe',
            ),
        )

    def __str__(self) -> str:
        return f'{self.user.username}, {self.recipe}'


class Favorite(models.Model):
    """Модель избранного."""

    user = models.ForeignKey(
        User,
        related_name='favorite',
        on_delete=models.CASCADE,
        verbose_name='Пользователь')
    recipe = models.ForeignKey(
        Recipe,
        related_name='favorite',
        on_delete=models.CASCADE,
        verbose_name='Рецепт')

    class Meta:
        verbose_name_plural = 'Избранное'
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique_favorite',
            ),
        )

    def __str__(self) -> str:
        return f'{self.user.username}, {self.recipe}'
