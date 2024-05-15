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
  unit = models.CharField(max_length=50)

  def __str__(self):
    return f"{self.quantity} {self.unit} {self.name}"


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
  raw_ingredients = models.TextField()
  ingredients = models.ManyToManyField(Ingredient, related_name='recipes')
  preparation = models.TextField()
  image = models.ImageField(upload_to='recepies/', null=True, blank=True) 
  categories = models.ManyToManyField(Category, related_name='recipes')
  ratings = models.JSONField(default=dict)
  average_rating = models.FloatField(default=0.0)
  created_at = models.DateTimeField(auto_now_add=True)
  creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name="creator_recipe")
  comments = models.ManyToManyField('Comment', related_name="comments_on_recipe", blank=True)


  def update_rating(self, user, new_rating):
    rating_obj, created = Rating.objects.get_or_create(user=user, recipe=self, defaults={'score': new_rating})
    if not created:
        rating_obj.score = new_rating
        rating_obj.save()
    self._update_average_rating()

  def _update_average_rating(self):
      all_ratings = self.recipe_ratings.all()
      total_rating = sum(rating.score for rating in all_ratings)
      total_votes = all_ratings.count()
      self.average_rating = total_rating / total_votes if total_votes else 0
      self.save()

  def __str__(self):
    return self.title

  
  def get_preparation_section(self):
        return self.preparation.split('\n') 
  
  def get_absolute_url(self):
        return reverse('recipe_detail', kwargs={'pk': self.pk})
  
class Rating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_ratings")
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name="recipe_ratings")
    score = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])

    class Meta:
        unique_together = ('user', 'recipe')  # Biztosítja, hogy minden felhasználó csak egyszer értékeljen egy receptet

class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    recipe = models.ForeignKey('Recipe', on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'recipe')

    def __str__(self):
        return f'{self.user.username} - {self.recipe.title}'

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

