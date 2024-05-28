from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

from .forms import RatingForm, CommentForm, FridgeForm, RecipeForm
from .models import Recipe, ShoppingList, ShoppingListItem, Category, Ingredient, Rating, Favorite, Comment
from .utils import paginate_with_page_range, get_categories_and_shopping_list_count, handle_ingredient_operation, get_ratings_info, parse_ingredients
from django.db.models import Q




def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "recepies/register.html", {"message": "Passwords must match."})

        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "recepies/register.html", {"message": "Username already taken."})
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "recepies/register.html")

def login_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "recepies/login.html", {"message": "Invalid username and/or password."})
    else:
        return render(request, "recepies/login.html")

def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))

def index(request):
    categories, shopping_list_items_count = get_categories_and_shopping_list_count(request.user)
    recipes = Recipe.objects.all().order_by('-created_at')
    paginated_recipes, page_range, last_two_pages = paginate_with_page_range(request, recipes, per_page=12)

    return render(request, 'recepies/index.html', {
        'categories': categories,
        'recipes': paginated_recipes,
        'page_range': page_range,
        'last_two_pages': last_two_pages,
        'shopping_list_items_count': shopping_list_items_count,
    })

def recipe_add(request):
    categories, shopping_list_items_count = get_categories_and_shopping_list_count(request.user)
    if request.method == 'POST':
        form = RecipeForm(request.POST, request.FILES)
        if form.is_valid():
            new_recipe = form.save(commit=False)
            new_recipe.creator = request.user
            new_recipe.save()
            raw_ingredients = form.cleaned_data['raw_ingredients']
            ingredients_data = parse_ingredients(raw_ingredients)
            for quantity, unit, name in ingredients_data:
                ingredient, created = Ingredient.objects.get_or_create(name=name.strip(), defaults={'quantity': quantity, 'unit': unit})
                new_recipe.ingredients.add(ingredient)
            new_recipe.save()
            form.save_m2m()
            return redirect('index')
    else:
        form = RecipeForm()
    return render(request, 'recepies/recipe_form.html', {
        'form': form, 'categories': categories, 'shopping_list_items_count': shopping_list_items_count,
    })



def edit_recipe(request, recipe_id):
    categories, shopping_list_items_count = get_categories_and_shopping_list_count(request.user)
    recipe = get_object_or_404(Recipe, pk=recipe_id)
    if request.method == 'POST':
        form = RecipeForm(request.POST, request.FILES, instance=recipe)
        if form.is_valid():
            updated_recipe = form.save(commit=False)
            updated_recipe.save()
            updated_recipe.ingredients.clear()
            raw_ingredients = form.cleaned_data['raw_ingredients']
            ingredients_data = parse_ingredients(raw_ingredients)
            for quantity, unit, name in ingredients_data:
                ingredient, created = Ingredient.objects.get_or_create(name=name.strip(), defaults={'quantity': quantity, 'unit': unit})
                if not created:
                    ingredient.quantity = quantity
                    ingredient.unit = unit
                    ingredient.save()
                updated_recipe.ingredients.add(ingredient)
            updated_recipe.save()
            form.save_m2m()
            return redirect('recipe_details', recipe_id=recipe_id)
    else:
        form = RecipeForm(instance=recipe)
    return render(request, 'recepies/edit_recipe.html', {
        'form': form, 'recipe': recipe, 'categories': categories, 'shopping_list_items_count': shopping_list_items_count,
    })

def my_recipes(request):
    categories, shopping_list_items_count = get_categories_and_shopping_list_count(request.user)
    recipes = Recipe.objects.filter(creator=request.user)
    paginated_recipes, page_range, last_two_pages = paginate_with_page_range(request, recipes, per_page=12)

    return render(request, 'recepies/my_recipes.html', {
        'categories': categories, 'recipes': paginated_recipes, 'page_range': page_range, 'last_two_pages': last_two_pages, 'shopping_list_items_count': shopping_list_items_count,
    })

def recipe_details(request, recipe_id):
    categories, shopping_list_items_count = get_categories_and_shopping_list_count(request.user)
    recipe = get_object_or_404(Recipe, pk=recipe_id)
    already_rated = False
    user_favorite_recipes = []

    if request.user.is_authenticated:
        user_favorite_recipes = [fav.recipe for fav in Favorite.objects.filter(user=request.user)]
        already_rated = Rating.objects.filter(user=request.user, recipe=recipe).exists()

    ratings, total_ratings = get_ratings_info(recipe)

    comment_form = CommentForm()

    if request.method == 'POST' and request.user.is_authenticated:
        if "comment_form" in request.POST:
            comment_form = CommentForm(request.POST)
            if comment_form.is_valid():
                comment = comment_form.cleaned_data["content"]
                new_comment = Comment(recipe=recipe, user=request.user, content=comment)
                new_comment.save()
                recipe.comments.add(new_comment)
                recipe.save()
                return HttpResponseRedirect(reverse('recipe_details', args=[recipe_id]) + '?submitted=true')

        elif "ratings" in request.POST:
            form = RatingForm(request.POST)
            if form.is_valid() and not already_rated:
                new_rating = form.cleaned_data['ratings']
                Rating.objects.create(user=request.user, recipe=recipe, score=new_rating)
                recipe.update_rating(request.user, int(new_rating))
                return HttpResponseRedirect(reverse('recipe_details', args=[recipe_id]) + '?submitted=true')

    context = {
        "recipe": recipe,
        "user_favorite_recipes": user_favorite_recipes,
        'ratings': ratings,
        'total_ratings': total_ratings,
        'form': RatingForm(),
        'already_rated': already_rated,
        "commentForm": CommentForm(),
        "comments": recipe.comments.all().order_by('-created_at'),
        'categories': categories,
        'shopping_list_items_count': shopping_list_items_count,
    }

    return render(request, "recepies/recipe_details.html", context)



def recipes_by_category(request, category):
    categories, shopping_list_items_count = get_categories_and_shopping_list_count(request.user)
    category = Category.objects.get(title=category)
    recipes = Recipe.objects.filter(categories=category).order_by('title')
    paginated_recipes, page_range, last_two_pages = paginate_with_page_range(request, recipes, per_page=12)

    return render(request, 'recepies/recipes_by_category.html', {
        'categories': categories, 'category': category, 'recipes': paginated_recipes, 'page_range': page_range, 'last_two_pages': last_two_pages, 'shopping_list_items_count': shopping_list_items_count,
    })

def search(request):
    categories, shopping_list_items_count = get_categories_and_shopping_list_count(request.user)
    query = request.GET.get('query', '')
    if query:
        recipes = Recipe.objects.filter(title__icontains=query)
    else:
        recipes = Recipe.objects.none()

    paginated_recipes, page_range, last_two_pages = paginate_with_page_range(request, recipes, per_page=12)

    return render(request, 'recepies/search.html', {
        'categories': categories, 'query': query, 'recipes': paginated_recipes, 'page_range': page_range, 'last_two_pages': last_two_pages, 'shopping_list_items_count': shopping_list_items_count,
    })

def add_to_shopping_list(request, recipe_id, ingredient_name):
    return handle_ingredient_operation(request, recipe_id, ingredient_name, 'add')

def remove_from_shopping_list(request, recipe_id, ingredient_name):
    return handle_ingredient_operation(request, recipe_id, ingredient_name, 'remove')

def view_shopping_list(request):
    categories, shopping_list_items_count = get_categories_and_shopping_list_count(request.user)
    shopping_list, created = ShoppingList.objects.get_or_create(user=request.user)
    return render(request, 'recepies/shopping_list.html', {
        'shopping_list': shopping_list, 'categories': categories, 'shopping_list_items_count': shopping_list_items_count,
    })

def delete_list_item(request, item_id):
    if request.method == 'POST':
        list_item = ShoppingListItem.objects.get(id=item_id)
        shopping_list = list_item.shopping_list
        list_item.delete()
        shopping_list_items_count = shopping_list.ingredients.count()
        return JsonResponse({'status': 'success', 'shopping_list_items_count': shopping_list_items_count})
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)

def add_to_favorites(request, recipe_id):
    if request.method == "POST":
        recipe = get_object_or_404(Recipe, pk=recipe_id)
        favorite, created = Favorite.objects.get_or_create(user=request.user, recipe=recipe)
        if not created:
            favorite.delete()
            return JsonResponse({"success": True, "favorited": False})
        else:
            return JsonResponse({"success": True, "favorited": True})
    return JsonResponse({"success": False})

def list_favorites(request):
    categories, shopping_list_items_count = get_categories_and_shopping_list_count(request.user)
    favorites = Favorite.objects.filter(user=request.user).select_related('recipe')
    paginated_favorites, page_range, last_two_pages = paginate_with_page_range(request, [fav.recipe for fav in favorites], per_page=12)

    return render(request, 'recepies/favorites.html', {
        'categories': categories, 'recipes': paginated_favorites, 'page_range': page_range, 'last_two_pages': last_two_pages, 'shopping_list_items_count': shopping_list_items_count,
    })

def your_fridge(request):
    categories, shopping_list_items_count = get_categories_and_shopping_list_count(request.user)
    fridge_ingredients = []
    matching_recipes = None
    paginated_recipes = None
    page_range = None
    last_two_pages = None
    submitted = request.POST.get('submitted', False)

    if request.method == "POST":
        fridgeForm = FridgeForm(request.POST)
        if fridgeForm.is_valid():
            ingredient_1 = fridgeForm.cleaned_data['ingredient_1']
            ingredient_2 = fridgeForm.cleaned_data['ingredient_2']
            ingredient_3 = fridgeForm.cleaned_data['ingredient_3']
            ingredient_4 = fridgeForm.cleaned_data['ingredient_4']
            ingredient_5 = fridgeForm.cleaned_data['ingredient_5']
            ingredient_6 = fridgeForm.cleaned_data['ingredient_6']

            fridge_ingredients = [ingredient_1, ingredient_2, ingredient_3, ingredient_4, ingredient_5, ingredient_6]
            queries = [Q(raw_ingredients__icontains=ingredient) for ingredient in fridge_ingredients if ingredient]
            if queries:
                query = queries.pop()
                for item in queries:
                    query |= item

                matching_recipes = Recipe.objects.filter(query).distinct()
                paginated_recipes, page_range, last_two_pages = paginate_with_page_range(request, matching_recipes, per_page=12)
            else:
                matching_recipes = []

        fridgeForm = FridgeForm()
    else:
        fridgeForm = FridgeForm()

    context = {
        'fridgeForm': fridgeForm,
        'matching_recipes': paginated_recipes,
        'categories': categories,
        'page_range': page_range,
        'last_two_pages': last_two_pages,
        'shopping_list_items_count': shopping_list_items_count,
        'submitted': submitted,
    }

    return render(request, "recepies/your_fridge.html", context)