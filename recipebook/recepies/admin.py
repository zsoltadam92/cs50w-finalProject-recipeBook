from django.contrib import admin

from .models import  Recipe, Comment, Category, ShoppingList, ShoppingListItem

# Register your models here.
admin.site.register(Recipe)
admin.site.register(Comment)
admin.site.register(Category)
admin.site.register(ShoppingList)
admin.site.register(ShoppingListItem)