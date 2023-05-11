import os
import datetime
from django.http import FileResponse

from foodgram import settings
from recipes.models import Ingredient, RecipeIngredients, GroceryList


def download_shopping_cart(request):
    user = request.user
    file_path = os.path.join(
        settings.MEDIA_ROOT,
        'recipes/shopping_cart/',
        str(user)
    )

    os.makedirs(file_path, exist_ok=True)
    file = os.path.join(
        file_path,
        str(datetime.datetime.now()) + '.txt'
    )

    purchases = GroceryList.objects.filter(user=user)

    with open(file, 'w') as f:
        cart = dict()
        for purchase in purchases:
            ingredients = RecipeIngredients.objects.filter(
                recipe=purchase.recipe.id
            )
            for r in ingredients:
                i = Ingredient.objects.get(pk=r.ingredient.id)
                point_name = f'{i.name} ({i.measurement_unit})'
                if point_name in cart.keys():
                    cart[point_name] += r.amount
                else:
                    cart[point_name] = r.amount

        for name, amount in cart.items():
            f.write(f'* {name} - {amount}\n')

    return FileResponse(open(file, 'rb'), as_attachment=True)