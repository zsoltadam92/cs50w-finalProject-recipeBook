from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

from .models import Recipe, Comment, Category
from .forms import RecipeForm
from .forms import RatingForm


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
    categories = Category.objects.all()
    if request.method == 'POST':
        form = RecipeForm(request.POST, request.FILES)
        if form.is_valid():
            # Létrehozunk egy új recept példányt a form adataival, de még nem mentjük el.
            new_recipe = form.save(commit=False)
            # Beállítjuk a recept létrehozóját a jelenlegi felhasználóra.
            new_recipe.creator = request.user
            # Most már elmentjük az adatbázisba.
            new_recipe.save()
            # Mivel a categories egy ManyToManyField, ezt csak a példány mentése után állíthatjuk be.
            form.save_m2m()
            return redirect('index')
    else:
        form = RecipeForm()
    return render(request, 'recepies/recipe_form.html', {'form': form, 'categories': categories})


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
    




# new_recipe = Recipe(
#                 title=form.cleaned_data["title"],
#                 serving=form.cleaned_data["serving"],
#                 preparation_time=form.cleaned_data['preparation_time'],
#                 difficulty=form.cleaned_data['difficulty'],
#                 ingredients=form.cleaned_data['ingredients'],
#                 preparation=form.cleaned_data['preparation'],
#                 image=form.cleaned_data['image'],
#                 categories=form.cleaned_data['categories'],
#                 creator=request.user, 
#             )

#             new_recipe.save()