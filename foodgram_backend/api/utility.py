from django.http import HttpResponse
from django.db.models import Sum

from recipes.models import IngredientRecipe


def download_shopping_list(request):
    ingredient_list = "Cписок покупок:"
    ingredients = IngredientRecipe.objects.filter(
        recipe__shopping_cart__user=request.user
    ).values(
        'ingredient__name', 'ingredient__measurement_unit'
    ).annotate(ingredient_amount=Sum('amount'))
    for ing_nums, ingredient in enumerate(ingredients):
        ingredient_list += (
            f"\n{ingredient['ingredient__name']} - "
            f"{ingredient['ingredient_amount']} "
            f"{ingredient['ingredient__measurement_unit']}"
        )
        if ing_nums < ingredients.count() - 1:
            ingredient_list += ', '
    filename = 'shopping_list.txt'
    response = HttpResponse(ingredient_list, content_type='text/plain')
    response['Content-Disposition'] = (
        'attachment; filename={0}'.format(filename)
    )
    return response
