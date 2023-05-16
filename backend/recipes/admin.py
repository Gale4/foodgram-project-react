from django.contrib import admin

from recipes.models import (Favorite, GroceryList, Ingredient, Recipe,
                            RecipeIngredients, Tag)


class IngredientAmountInline(admin.TabularInline):
    min_num = 1
    model = RecipeIngredients


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author', 'favorite_count')
    list_filter = ('author', 'name', 'tags')
    filter_horizontal = ('tags',)
    inlines = (IngredientAmountInline,)

    def favorite_count(self, obj):
        return obj.favorite.count()


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    list_filter = ('name',)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'slug')


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'user')


@admin.register(GroceryList)
class GroceryListAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'user')
