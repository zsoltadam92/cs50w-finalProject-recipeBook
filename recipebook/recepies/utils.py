from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

def paginate_recipes(request, recipes, per_page):
    paginator = Paginator(recipes, per_page)
    page = request.GET.get('page')
    
    try:
        paginated_recipes = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        paginated_recipes = paginator.page(1)
    except EmptyPage:
        # If page is out of range, deliver last page of results.
        paginated_recipes = paginator.page(paginator.num_pages)

    return paginated_recipes


def get_page_range(current_page, last_page, window=2):
    """
    Generate a range of page numbers for pagination.
    `window` specifies how many pages to show on each side of the current page.
    """
    start = max(current_page - window, 1)
    end = min(current_page + window, last_page) + 1
    return range(start, end)


