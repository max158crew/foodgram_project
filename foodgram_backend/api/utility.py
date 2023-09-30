from django.http import HttpResponse
from recipes.models import ShoppingCart


def download_shopping_list(request):
    shopping_cart = ShoppingCart.objects.filter(user=request.user).all()
    shopping_list = {}
    for item in shopping_cart:
        for ingredients in item.recipe.ingridients_in_recipe.all():
            name = ingredients.ingredient.name
            measuring_unit = ingredients.ingredient.measurement_unit
            amount = ingredients.amount
            if name not in shopping_list:
                shopping_list[name] = {
                    'name': name,
                    'measurement_unit': measuring_unit,
                    'amount': amount
                }
            else:
                shopping_list[name]['amount'] += amount
    content = (
        [f'{item["name"]} ({item["measurement_unit"]}) '
         f'- {item["amount"]}\n'
         for item in shopping_list.values()]
    )
    filename = 'shopping_list.txt'
    response = HttpResponse(content, content_type='text/plain')
    response['Content-Disposition'] = (
        'attachment; filename={0}'.format(filename)
    )
    return response