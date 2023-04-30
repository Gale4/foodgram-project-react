from django.db import models
from users.models import User


class Tag(models.Model):
    name = models.CharField(max_length=200)
    color = models.CharField(max_length=7)
    slug = models.SlugField(unique=True)

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(max_length=200)
    measurement_unit = models.CharField(max_length=200)

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Recipe(models.Model):
    name = models.CharField('Название', max_length=200, db_index=True)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes'
        )
    
    text = models.TextField(blank=False)

    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredients'
    )

    tags = models.ManyToManyField(
        Tag,
        through='TagRecipe'
    )

    image = models.ImageField(
        upload_to='recipes/',
        null=False,
        blank=False
    )

    cooking_time = models.PositiveSmallIntegerField(blank=False)

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class RecipeIngredients(models.Model):
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    amount = models.CharField(max_length=200, blank=False)

    def __str__(self):
        return f'{self.recipe} {self.ingredient}'


class TagRecipe(models.Model):
    tags = models.ForeignKey(Tag, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.tags} {self.recipe}'