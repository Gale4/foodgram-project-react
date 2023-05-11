from django.contrib import admin

from .models import (
    Favorite, Ingredient, Recipe,
    RecipeIngredients, Tag, GroceryList
)


class IngredientAmountInline(admin.TabularInline):
    min_num = 1
    model = RecipeIngredients

class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author')
    list_filter = ('author', 'name', 'tags')
    filter_horizontal = ('tags',)
    inlines = (IngredientAmountInline,)

    #def favorite_count(self, obj):
    #    return obj.favorites.count()

class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    list_filter = ('name',)

class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'slug')

class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'user')

class GroceryListAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'user')

admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Favorite, FavoriteAdmin)
admin.site.register(GroceryList, GroceryListAdmin)
