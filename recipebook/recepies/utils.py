from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import Category, ShoppingList

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