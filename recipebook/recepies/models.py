from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.

class User(AbstractUser):
  pass

# Difficulty levels for the dropdown menu
class DifficultyLevel(models.TextChoices):
  EASY= 'Easy'
  MEDIUM = 'Medium'
  HARD = 'Hrd'

class Recipe(models.Model):
  title = models.CharField(max_length=128)
  serving = models.PositiveIntegerField()
  preparation_time = models.PositiveIntegerField()
  difficulty = models.CharField(
    choices=DifficultyLevel.choices,
    default=DifficultyLevel.EASY
  )
  ingredients = models.TextField()
  preparation = models.TextField()

class Comment(models.Model):
  user = models.ForeignKey(User, on_delete=models.CASCADE)
  recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
  content = models.TextField()
  created_at = models.DateTimeField(auto_now_add=True)

class Category(models.Model):
  title = models.CharField(max_length=100)