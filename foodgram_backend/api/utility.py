from django.http import HttpResponse
from recipes.models import ShoppingCart


def download_shopping_list(request):
    shopping_cart = ShoppingCart.objects.filter(user=request.user).all()
    shopping_items = {}
    for item in shopping_cart:
        for ingredients in item.recipe.ingredients_in_recipe.all():
            name = ingredients.ingredient.name
            measuring_unit = ingredients.ingredient.measurement_unit
            amount = ingredients.amount
            if name not in shopping_items:
                shopping_items[name] = {
                    'name': name,
                    'measure': measuring_unit,
                    'amount': amount
                }
            else:
                shopping_items[name]['amount'] += amount
    content = (
        [f'{item["name"]} ({item["measure"]}) '
         f'- {item["amount"]}\n'
         for item in shopping_items.values()]
    )
    filename = 'shopping_list.txt'
    response = HttpResponse(content, content_type='text/plain')
    response['Content-Disposition'] = (
        'attachment; filename={0}'.format(filename)
    )
    return response
