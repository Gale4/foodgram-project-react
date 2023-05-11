from django.db import models

from users.models import User


class Tag(models.Model):
    """Модель тега."""

    name = models.CharField(max_length=200, unique=True)
    color = models.CharField(max_length=7, unique=True)
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
        constraints = (
            models.UniqueConstraint(
                fields=('name', 'measurement_unit'),
                name='unique_ingredients',
            ),
        )
    
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
        related_name='recipes',
        verbose_name='Автор',
    )
    
    text = models.TextField(blank=False)

    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredients',
        verbose_name='Ингредиенты'
    )

    tags = models.ManyToManyField(Tag, through='TagRecipe')

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


class TagRecipe(models.Model):
    """Связь тега с рецептом."""

    tag = models.ForeignKey(
        Tag,
        on_delete=models.CASCADE,
        related_name='tag_recipe'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='tags_recipe'
    )
    
    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=('recipe_id', 'tag_id'),
                name='unique_tag',
            ),
        )

    def __str__(self):
        return f'{self.tag} {self.recipe}'


class RecipeIngredients(models.Model):
    """Связь ингредиента с рецептом."""

    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='in_recipe'
    )
    
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='ingredients_in'
    )
    
    amount = models.IntegerField(default=1)

    class Meta:
        verbose_name = 'Количество'
    
    def __str__(self):
        return f'{self.recipe} {self.ingredient}'


class GroceryList(models.Model):
    """Модель списка покупок."""

    user = models.ForeignKey(
        User,
        related_name='in_grocery_list',
        on_delete=models.CASCADE
    )
    recipe = models.ForeignKey(
        Recipe,
        related_name='in_grocery_list',
        on_delete=models.CASCADE
        )

    class Meta:
        verbose_name_plural = 'Корзина покупок'
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique_recipe',
            ),
        )


class Favorite(models.Model):
    """Модель избранного."""

    user = models.ForeignKey(
        User,
        related_name='favorite',
        on_delete=models.CASCADE
    )
    recipe = models.ForeignKey(
        Recipe,
        related_name='favorite',
        on_delete=models.CASCADE
        )
    
    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique_favorite',
            ),
        )