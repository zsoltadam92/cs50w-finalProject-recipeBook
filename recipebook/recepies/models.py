from django.contrib.auth.models import User
from django.db import models

# Create your models here.

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
  ingredients = models.TextField()
  preparation = models.TextField()

class Comment(models.Model):
  user = models.ForeignKey(User, on_delete=models.CASCADE,related_name="user")
  recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name="comment")
  content = models.TextField()
  created_at = models.DateTimeField(auto_now_add=True)

class Category(models.Model):
  title = models.CharField(max_length=100)