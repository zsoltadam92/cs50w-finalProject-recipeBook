from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path('recipe/add/', views.recipe_add, name='recipe_add'),
    path('recipe/<int:recipe_id>', views.recipe_details, name='recipe_details'),
    path('category/<str:category>/',views.recipes_by_category, name='recipes_by_category'),
    path('search/',views.search, name='search'),

] 

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)