from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import JsonResponse
from .models import Category, ShoppingList, Ingredient
from urllib.parse import unquote
from fractions import Fraction



def parse_ingredients(raw_ingredients):
    ingredients = []
    lines = raw_ingredients.split('\n')
    for line in lines:
        parts = line.split(maxsplit=2)
        if len(parts) >= 2:
            try:
                quantity = float(Fraction(parts[0]))
                if len(parts) == 2:
                    unit = ''
                    name = parts[1]
                else:
                    unit = parts[1]
                    name = parts[2]
                ingredients.append((quantity, unit, name))
            except ValueError:
                continue
    return ingredients


def get_ratings_info(recipe):
    ratings = {str(i): 0 for i in range(5, 0, -1)}
    for rating in recipe.recipe_ratings.all():
        ratings[str(rating.score)] += 1
    total_ratings = sum(ratings.values())
    return ratings, total_ratings


def paginate_with_page_range(request, queryset, per_page):
    """
    Paginates the queryset and generates a page range including the last two pages.
    """
    paginator = Paginator(queryset, per_page)
    page = request.GET.get('page')

    try:
        paginated_queryset = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver the first page.
        paginated_queryset = paginator.page(1)
    except EmptyPage:
        # If page is out of range, deliver the last page of results.
        paginated_queryset = paginator.page(paginator.num_pages)

    # Determine the page range
    current_page = paginated_queryset.number
    last_page = paginator.num_pages
    window = 2

    # Basic page range logic
    start_page = max(current_page - window, 1)
    end_page = min(current_page + window, last_page) + 1
    page_range = range(start_page, end_page)

    # Always include the last two pages
    if last_page > 2:
        last_two_pages = range(last_page - 1, last_page + 1)
    else:
        last_two_pages = range(1, last_page + 1)

    return paginated_queryset, page_range, last_two_pages


def get_categories_and_shopping_list_count(user):
    categories = Category.objects.all()
    shopping_list_items_count = 0

    if user.is_authenticated:
        try:
            shopping_list = ShoppingList.objects.get(user=user)
            shopping_list_items_count = shopping_list.ingredients.count()
        except ShoppingList.DoesNotExist:
            shopping_list_items_count = 0

    return categories, shopping_list_items_count


def get_or_create_shopping_list(user):
    return ShoppingList.objects.get_or_create(user=user)

def get_ingredient(name):
    return Ingredient.objects.get(name=name)

def json_response(status, message=None, shopping_list_items_count=None):
    response_data = {'status': status}
    if message:
        response_data['message'] = message
    if shopping_list_items_count is not None:
        response_data['shopping_list_items_count'] = shopping_list_items_count
    return JsonResponse(response_data)

def handle_ingredient_operation(request, recipe_id, ingredient_name, operation):
    if request.method != 'POST':
        return json_response('error', 'Invalid request', status=400)

    user = request.user
    ingredient_name = unquote(ingredient_name)

    try:
        shopping_list, _ = get_or_create_shopping_list(user)
        ingredient = get_ingredient(ingredient_name)
    except Ingredient.DoesNotExist:
        return json_response('error', 'Ingredient does not exist', status=400)

    if operation == 'add':
        if shopping_list.ingredients.filter(id=ingredient.id).exists():
            return json_response('exists', 'Ingredient is already in the shopping list')
        shopping_list.ingredients.add(ingredient)
    elif operation == 'remove':
        if not shopping_list.ingredients.filter(id=ingredient.id).exists():
            return json_response('error', 'Ingredient not in the shopping list', status=400)
        shopping_list.ingredients.remove(ingredient)

    shopping_list_items_count = shopping_list.ingredients.count()
    return json_response('success', shopping_list_items_count=shopping_list_items_count)
