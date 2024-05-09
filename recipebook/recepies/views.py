from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from fractions import Fraction

from .forms import RatingForm, CommentForm, FridgeForm, RecipeForm
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from .models import Recipe, ShoppingList, ShoppingListItem, Category, Ingredient, Rating, Favorite, Comment
from django.views.decorators.http import require_http_methods
from django.db.models import Q
from .utils import paginate_with_page_range
import json


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "recepies/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "recepies/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "recepies/register.html")

def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "recepies/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "recepies/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))

def index(request):
    categories = Category.objects.all()
    recipes = Recipe.objects.all().order_by('created_at')
    paginated_recipes, page_range, last_two_pages = paginate_with_page_range(request, recipes, per_page=12)

    return render(request, 'recepies/index.html', {
        'categories': categories,
        'recipes': paginated_recipes,
        'page_range': page_range,
        'last_two_pages': last_two_pages,
    })


def recipe_add(request):
    categories = Category.objects.all()
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
    return render(request, 'recepies/recipe_form.html', {'form': form, 'categories': categories,})


def parse_ingredients(raw_ingredients):
    ingredients = []
    lines = raw_ingredients.split('\n')
    for line in lines:
        parts = line.split(maxsplit=2) 
        if len(parts) >= 3:
            try:
                quantity = float(Fraction(parts[0])) 
            except ValueError:
                continue 
            unit = parts[1]
            name = parts[2]
            ingredients.append((quantity, unit, name))
    return ingredients

def edit_recipe(request, recipe_id):
    categories = Category.objects.all()
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
                updated_recipe.ingredients.add(ingredient)
            updated_recipe.save()
            form.save_m2m() 
            return redirect('recipe_details', recipe_id=recipe_id)
    else:
        form = RecipeForm(instance=recipe)
    return render(request, 'recepies/edit_recipe.html', {'form': form, 'recipe': recipe, 'categories': categories})


def my_recipes(request):
    categories = Category.objects.all()
    recipes = Recipe.objects.filter(creator=request.user)
    paginated_recipes, page_range, last_two_pages = paginate_with_page_range(request, recipes, per_page=12)

    return render(request, 'recepies/my_recipes.html', {
        'categories': categories, 
        'recipes': paginated_recipes,
        'page_range': page_range,
        'last_two_pages': last_two_pages,
        })


def recipe_details(request, recipe_id):
    categories = Category.objects.all()
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

        elif "ratings" in request.POST:
            form = RatingForm(request.POST)
            if form.is_valid() and not already_rated:
                new_rating = form.cleaned_data['ratings']
                Rating.objects.create(user=request.user, recipe=recipe, score=new_rating)
                recipe.update_rating(request.user, int(new_rating))
                return redirect('recipe_details', recipe_id=recipe_id)
            else:
                form = RatingForm() if request.user.is_authenticated else None

    context = {
        "recipe": recipe,
        "user_favorite_recipes": user_favorite_recipes,
        'ratings': ratings,
        'total_ratings': total_ratings,
        'form': RatingForm(),
        'already_rated': already_rated,
        "commentForm": CommentForm(),
        "comments": recipe.comments.all().order_by('-created_at'),
        'categories': categories
    }

    return render(request, "recepies/recipe_details.html", context)

def get_ratings_info(recipe):
    ratings = {str(i): 0 for i in range(5, 0, -1)}
    for rating in recipe.recipe_ratings.all():
        ratings[str(rating.score)] += 1 
    total_ratings = sum(ratings.values())
    return ratings, total_ratings



def recipes_by_category(request, category):
    categories = Category.objects.all()
    category = Category.objects.get(title=category)
    recipes = Recipe.objects.filter(categories=category).order_by('title')  
    paginated_recipes, page_range, last_two_pages = paginate_with_page_range(request, recipes, per_page=12)

    return render(request, 'recepies/recipes_by_category.html', {
        'categories': categories, 
        'category': category,
        'recipes': paginated_recipes,
        'page_range': page_range,
        'last_two_pages': last_two_pages,
        })

def search(request):
    categories = Category.objects.all()
    query = request.GET.get('query', '')
    if query:
        recipes = Recipe.objects.filter(title__icontains=query)
    else:
        recipes = Recipe.objects.none()

    paginated_recipes, page_range, last_two_pages = paginate_with_page_range(request, recipes, per_page=12)

    return render(request, 'recepies/search.html', {
        'categories': categories, 
        'query': query,
        'recipes': paginated_recipes,
        'page_range': page_range,
        'last_two_pages': last_two_pages,
        })



def add_to_shopping_list(request, recipe_id, ingredient_name):
    if not request.user.is_authenticated:
        return JsonResponse({'status': 'error', 'message': 'Not logged.'}, status=403)

    try:
        recipe = Recipe.objects.get(pk=recipe_id)
        ingredient = recipe.ingredients.get(name=ingredient_name)
        shopping_list, created = ShoppingList.objects.get_or_create(user=request.user)

        if ShoppingListItem.objects.filter(shopping_list=shopping_list, ingredient=ingredient).exists():
            return JsonResponse({'status': 'error', 'message': 'Ingredient already in the list'})

        ShoppingListItem.objects.create(shopping_list=shopping_list, ingredient=ingredient)
        return JsonResponse({'status': 'success'})
    except Recipe.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Recipe not found'}, status=404)
    except Ingredient.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Hozzávaló nem található'}, status=404)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    
def view_shopping_list(request):
    categories = Category.objects.all()
    shopping_list, created = ShoppingList.objects.get_or_create(user=request.user)
    return render(request, 'recepies/shopping_list.html', {'shopping_list': shopping_list, 'categories': categories})

def delete_list_item(request, item_id):
    if request.method == 'POST':
        item = get_object_or_404(ShoppingListItem, pk=item_id)
        item.delete()
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)

def remove_from_shopping_list(request, recipe_id, ingredient_name):
    if request.method == 'POST':
        try:
            recipe = Recipe.objects.get(pk=recipe_id)
            ingredient = recipe.ingredients.get(name=ingredient_name)
            shopping_list_item = ShoppingListItem.objects.get(
                shopping_list__user=request.user, 
                ingredient=ingredient
            )
            shopping_list_item.delete()
            return JsonResponse({'status': 'success'})
        except (Recipe.DoesNotExist, Ingredient.DoesNotExist, ShoppingListItem.DoesNotExist):
            return JsonResponse({'status': 'error', 'message': 'Item not found'}, status=404)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

def add_to_favorites(request, recipe_id):
    recipe = get_object_or_404(Recipe, pk=recipe_id)
    if request.method == "POST":
        favorite, created = Favorite.objects.get_or_create(user=request.user, recipe=recipe)
        if not created:
            favorite.delete()
            messages.success(request, "Recipe removed from your favorites.")
        else:
            messages.success(request, "Recipe added to your favorites.")
        return redirect('recipe_details', recipe_id=recipe_id)
    return redirect('recipe_details', recipe_id=recipe_id)


def list_favorites(request):
    categories = Category.objects.all()
    favorites = Favorite.objects.filter(user=request.user).select_related('recipe')
    paginated_favorites, page_range, last_two_pages = paginate_with_page_range(request, [fav.recipe for fav in favorites], per_page=12)

    return render(request, 'recepies/favorites.html', {
        'categories': categories, 
        'recipes': paginated_favorites,
        'page_range': page_range,
        'last_two_pages': last_two_pages,
        })


def your_fridge(request):
    categories = Category.objects.all()
    fridge_ingredients = []
    matching_recipes = []

    if request.method == "POST":
        fridgeForm = FridgeForm(request.POST)
        if fridgeForm.is_valid():
            ingredient_1 = fridgeForm.cleaned_data['ingredient_1']
            ingredient_2 = fridgeForm.cleaned_data['ingredient_2']
            ingredient_3 = fridgeForm.cleaned_data['ingredient_3']
            ingredient_4 = fridgeForm.cleaned_data['ingredient_4']
            ingredient_5 = fridgeForm.cleaned_data['ingredient_5']

            fridge_ingredients = [ingredient_1, ingredient_2, ingredient_3, ingredient_4, ingredient_5]
            
            # Filter recipes that contain any of the ingredients listed in the fridge
            queries = [Q(raw_ingredients__icontains=ingredient) for ingredient in fridge_ingredients if ingredient]
            print(queries)
            query = queries.pop()
            for item in queries:
                query |= item
                

            matching_recipes = Recipe.objects.filter(query).distinct()

    else:
        fridgeForm = FridgeForm()
        
    context = {
        'fridgeForm': fridgeForm,
        'matching_recipes': matching_recipes,
        'categories': categories
        
    }

    return render(request, "recepies/your_fridge.html", context)

