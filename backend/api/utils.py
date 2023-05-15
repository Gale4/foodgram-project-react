from django.http import HttpResponse

from recipes.models import GroceryList, Ingredient, RecipeIngredients


def download_shopping_cart(request):
    """Возвращает текстовый фаил со списком ингредиентов из списка покупок."""
    grocery_list = GroceryList.objects.filter(user=request.user)
    shopping_list = dict()
    for purchase in grocery_list:
        ingredients = RecipeIngredients.objects.filter(
            recipe=purchase.recipe.id)
        for ing in ingredients:
            name = ing.ingredient.name
            measuring_unit = ing.ingredient.measurement_unit
            amount = ing.amount
            if name not in shopping_list:
                shopping_list[name] = {
                    'name': name,
                    'measurement_unit': measuring_unit,
                    'amount': amount
                }
            else:
                shopping_list[name]['amount'] += amount

    content = (
        [
            f'{item["name"]} ({item["measurement_unit"]}) - {item["amount"]}\n'
            for item in shopping_list.values()
        ])
    filename = 'shopping_list.txt'
    text_file = HttpResponse(content, content_type='text/plain')
    text_file['Content-Disposition'] = (
        'attachment; filename={0}'.format(filename))
    return text_file
