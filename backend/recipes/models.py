from django.db import models
from users.models import User



class Tag(models.Model):
    """Модель тега."""

    name = models.CharField(max_length=200)
    color = models.CharField(max_length=7)
    slug = models.SlugField(unique=True)

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """Модель ингредиента."""

    name = models.CharField(max_length=200)
    measurement_unit = models.CharField(max_length=200)

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Recipe(models.Model):
    """Модель рецепта."""

    name = models.CharField(
        max_length=200,
        verbose_name='Название'
        )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes'
        )
    text = models.TextField(blank=False)
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredients',
        related_name='recipes'
        )

    tags = models.ManyToManyField(Tag)

    image = models.ImageField(
        upload_to='recipes/images/',
        null=False,
        default=None
    )

    cooking_time = models.PositiveSmallIntegerField(
        default=1,
        blank=False
    )

    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата рецепта'
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ['-pub_date']

    def __str__(self):
        return self.name


class RecipeIngredients(models.Model):
    """Связь ингредиента с рецептом."""

    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='ingredient_amount',
        )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='ingredient_amount',
        )
    amount = models.PositiveSmallIntegerField(default=1)

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
    
    def __str__(self):
        return f'{self.recipe} {self.ingredient}'


class GroceryList(models.Model):
    """Модель списка покупок."""

    user = models.ForeignKey(
        User,
        related_name='is_in_shopping_cart',
        on_delete=models.CASCADE
     )
    recipe = models.ForeignKey(
        Recipe,
        related_name='is_in_shopping_cart',
        on_delete=models.CASCADE
     )

    class Meta:
        verbose_name = 'Корзина покупок'


class Favorite(models.Model):
    """Модель избранного."""

    user = models.ForeignKey(
        User,
        related_name='is_favorited',
        on_delete=models.CASCADE
        )
    recipe = models.ForeignKey(
        Recipe,
        related_name='is_favorited',
        on_delete=models.CASCADE
        )
    
    class Meta:
        verbose_name = 'Избранное'