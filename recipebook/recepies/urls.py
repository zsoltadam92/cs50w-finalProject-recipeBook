from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path('category/<str:category>/',views.recipes_by_category, name='recipes_by_category'),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("my_recipes", views.my_recipes, name="my_recipes"),
    path("register", views.register, name="register"),
    path('recipe/add/', views.recipe_add, name='recipe_add'),
    path('recipes/edit/<int:recipe_id>/', views.edit_recipe, name='edit_recipe'),
    path('recipe/<int:recipe_id>', views.recipe_details, name='recipe_details'),
    path('search/',views.search, name='search'),
    path('shopping-list/', views.view_shopping_list, name='view_shopping_list'),
    path('add-to-shopping-list/<int:recipe_id>/<path:ingredient_name>/', views.add_to_shopping_list, name='add_to_shopping_list'),
    path('remove-from-shopping-list/<int:recipe_id>/<path:ingredient_name>/', views.remove_from_shopping_list, name='remove_from_shopping_list'),
    path('delete-list-item/<int:item_id>/', views.delete_list_item, name='delete_list_item'),
    path('add-to-favorites/<int:recipe_id>/', views.add_to_favorites, name='add_to_favorites'),
    path('favorites/', views.list_favorites, name='favorites'),
    path('your_fridge/', views.your_fridge, name='your_fridge'),




] 

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)