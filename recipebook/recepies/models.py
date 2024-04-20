from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse
from django.core.validators import MaxValueValidator, MinValueValidator



# Create your models here.

class Category(models.Model):
  title = models.CharField(max_length=100)

  def __str__(self):
        return self.title
  
class Ingredient(models.Model):
 name = models.CharField(max_length=255, unique=True)
 quantity = models.CharField(max_length=100)

# Difficulty levels for the dropdown menu
class DifficultyLevel(models.TextChoices):
  EASY= 'Easy'
  MEDIUM = 'Medium'
  HARD = 'Hard'

class Recipe(models.Model):
  title = models.CharField(max_length=128)
  serving = models.PositiveIntegerField()
  preparation_time = models.PositiveIntegerField()
  difficulty = models.CharField(
    max_length=6,
    choices=DifficultyLevel.choices,
    default=DifficultyLevel.EASY
  )
  raw_ingredients = models.TextField(help_text="List ingredients as free text.")
  ingredients = models.ManyToManyField(Ingredient, related_name='recipes')
  preparation = models.TextField()
  image = models.ImageField(upload_to='recepies/', null=True, blank=True) 
  categories = models.ManyToManyField(Category, related_name='recipes')
  ratings = models.JSONField(default=dict)
  average_rating = models.FloatField(default=0.0)
  created_at = models.DateTimeField(auto_now_add=True)
  creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name="creator_recipe")


  def update_rating(self, new_rating):
    ratings = self.ratings.get(str(new_rating), 0)
    self.ratings[str(new_rating)] = ratings + 1
    total_rating = sum(int(rate) * count for rate, count in self.ratings.items())
    total_votes = sum(self.ratings.values())
    self.average_rating = total_rating / total_votes
    self.save()

  def __str__(self):
    return self.title

  def get_ingredients_list(self):
    return self.raw_ingredients.split('\n') 
  
  def get_preparation_section(self):
        return self.preparation.split('\n') 
  
  def get_absolute_url(self):
        return reverse('recipe_detail', kwargs={'pk': self.pk})
  

class ShoppingList(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='shopping_list')
    ingredients = models.ManyToManyField(Ingredient, through='ShoppingListItem')

class ShoppingListItem(models.Model):
    shopping_list = models.ForeignKey(ShoppingList, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    purchased = models.BooleanField(default=False)

class Comment(models.Model):
  user = models.ForeignKey(User, on_delete=models.CASCADE,related_name="user")
  recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name="comment")
  content = models.TextField()
  created_at = models.DateTimeField(auto_now_add=True)

