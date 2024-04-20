from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

from .forms import RecipeForm
from .forms import RatingForm
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from .models import Recipe, ShoppingList, ShoppingListItem, Category, Ingredient
from django.views.decorators.http import require_http_methods


# Create your views here.

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
    recipes = Recipe.objects.all()
    return render(request, 'recepies/index.html', {'recipes': recipes, 'categories': categories})

def recipe_add(request):
    if request.method == 'POST':
        form = RecipeForm(request.POST, request.FILES)
        if form.is_valid():
            new_recipe = form.save(commit=False)
            new_recipe.creator = request.user
            new_recipe.save()
            # Feldolgozzuk a nyers összetevőket
            raw_ingredients = form.cleaned_data['raw_ingredients']
            ingredient_names = parse_ingredients(raw_ingredients)  # Implementáld ezt a függvényt a szöveg feldolgozására
            for name in ingredient_names:
                ingredient, created = Ingredient.objects.get_or_create(name=name.strip())
                new_recipe.ingredients.add(ingredient)
            new_recipe.save()
            form.save_m2m()
            return redirect('index')
    else:
        form = RecipeForm()
    return render(request, 'recepies/recipe_form.html', {'form': form})

def parse_ingredients(raw_ingredients):
    # Itt implementáld a szövegből összetevők kinyerését, pl. soronkénti feldolgozással
    return raw_ingredients.split('\n')

def my_recipes(request):
    recipes = Recipe.objects.filter(creator=request.user)
    return render(request, 'recepies/my_recipes.html', {"recipes": recipes})

def recipe_details(request, recipe_id):
    categories = Category.objects.all()
    recipe = Recipe.objects.get(pk=recipe_id)
    ratings = {str(i): 0 for i in range(5, 0, -1)}
    ratings.update(recipe.ratings)  
    total_ratings = sum(recipe.ratings.values())


    if request.method == 'POST':
        form = RatingForm(request.POST)
        if form.is_valid():
            form.save(recipe_id)
            return redirect('recipe_details', recipe_id=recipe_id)
    else:
        form = RatingForm() 

    return render(request, "recepies/recipe_details.html", {"recipe": recipe,'ratings': ratings, 'categories': categories, 'form': form, 'total_ratings': total_ratings})


def recipes_by_category(request, category):
    categories = Category.objects.all()
    category = Category.objects.get(title=category)
    recipes = Recipe.objects.filter(categories=category).order_by('title')  
    return render(request, 'recepies/recipes_by_category.html', {'recipes': recipes, 'category': category, 'categories': categories})

def search(request):
    categories = Category.objects.all()
    query = request.GET.get('query', '')
    if query:
        recipes = Recipe.objects.filter(title__icontains=query)
    else:
        recipes = Recipe.objects.none()
    return render(request, 'recepies/search.html', {'recipes': recipes, 'query': query, 'categories': categories})
    

def generate_shopping_list(request, recipe_id):
    try:
        recipe = Recipe.objects.get(pk=recipe_id)
        shopping_list, created = ShoppingList.objects.get_or_create(user=request.user)
        for ingredient in recipe.ingredients.all():
            ShoppingListItem.objects.create(shopping_list=shopping_list, ingredient=ingredient)
        return JsonResponse({'status': 'success', 'shopping_list_id': shopping_list.id})
    except Recipe.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Recipe not found'}, status=404)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    
def view_shopping_list(request):
    shopping_list, created = ShoppingList.objects.get_or_create(user=request.user)
    return render(request, 'recepies/shopping_list.html', {'shopping_list': shopping_list})

def delete_list_item(request, item_id):
    if request.method == 'POST':
        item = get_object_or_404(ShoppingListItem, pk=item_id)
        item.delete()
        return redirect('view_shopping_list')
    return redirect('view_shopping_list')

@require_http_methods(["POST"])
def toggle_purchased(request, item_id):
    item = get_object_or_404(ShoppingListItem, pk=item_id)
    item.purchased = not item.purchased
    item.save()
    return JsonResponse({'status': 'success', 'purchased': item.purchased})

