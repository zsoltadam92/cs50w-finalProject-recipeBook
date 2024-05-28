from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Recipe, Ingredient, Category, ShoppingList, Favorite, ShoppingListItem
from django.core.files.uploadedfile import SimpleUploadedFile


class RecepiesTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', email='test@example.com', password='password123')
        self.category = Category.objects.create(title="Test Category")

        # Create a temporary image file
        image = SimpleUploadedFile(name='test_image.jpg', content=b'', content_type='image/jpeg')

        self.recipe = Recipe.objects.create(
            title="Test Recipe",
            serving=2,
            preparation_time=30,
            difficulty="Easy",
            raw_ingredients="1 cup sugar\n2 cups flour",
            preparation="Mix ingredients and bake.",
            creator=self.user,
            image=image
        )
        self.recipe.categories.add(self.category)
        self.recipe.save()

    def test_register(self):
        response = self.client.post(reverse('register'), {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'password123',
            'confirmation': 'password123'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_login_view(self):
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'password123'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url, reverse('index'))

    def test_logout_view(self):
        self.client.login(username='testuser', password='password123')
        response = self.client.get(reverse('logout'))
        self.assertEqual(response.status_code, 302)
        self.assertFalse('_auth_user_id' in self.client.session)

    def test_index(self):
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Recipe")

    def test_recipe_add(self):
        self.client.login(username='testuser', password='password123')
        response = self.client.post(reverse('recipe_add'), {
            'title': 'New Recipe',
            'serving': 4,
            'preparation_time': 45,
            'difficulty': 'Medium',
            'raw_ingredients': '1 cup milk\n2 cups oats',
            'preparation': 'Mix and cook.',
            'categories': [self.category.id]
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Recipe.objects.filter(title='New Recipe').exists())

    def test_edit_recipe(self):
        self.client.login(username='testuser', password='password123')
        response = self.client.post(reverse('edit_recipe', args=[self.recipe.id]), {
            'title': 'Updated Recipe',
            'serving': 4,
            'preparation_time': 45,
            'difficulty': 'Medium',
            'raw_ingredients': '1 cup milk\n2 cups oats',
            'preparation': 'Mix and cook.',
            'categories': [self.category.id]
        })
        self.assertEqual(response.status_code, 302)
        self.recipe.refresh_from_db()
        self.assertEqual(self.recipe.title, 'Updated Recipe')

    def test_my_recipes(self):
        self.client.login(username='testuser', password='password123')
        response = self.client.get(reverse('my_recipes'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Recipe")

    def test_recipe_details(self):
        response = self.client.get(reverse('recipe_details', args=[self.recipe.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Recipe")

    def test_recipes_by_category(self):
        response = self.client.get(reverse('recipes_by_category', args=[self.category.title]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Recipe")

    def test_search(self):
        response = self.client.get(reverse('search'), {'query': 'Test'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Recipe")

    def test_add_to_shopping_list(self):
        self.client.login(username='testuser', password='password123')
        ingredient = Ingredient.objects.create(name='sugar', quantity=1, unit='cup')
        self.recipe.ingredients.add(ingredient)
        response = self.client.post(reverse('add_to_shopping_list', args=[self.recipe.id, ingredient.name]))
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {'status': 'success', 'shopping_list_items_count': 1})

    def test_remove_from_shopping_list(self):
        self.client.login(username='testuser', password='password123')
        ingredient = Ingredient.objects.create(name='sugar', quantity=1, unit='cup')
        shopping_list = ShoppingList.objects.create(user=self.user)
        shopping_list.ingredients.add(ingredient)
        response = self.client.post(reverse('remove_from_shopping_list', args=[self.recipe.id, ingredient.name]))
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {'status': 'success', 'shopping_list_items_count': 0})

    def test_view_shopping_list(self):
        self.client.login(username='testuser', password='password123')
        response = self.client.get(reverse('view_shopping_list'))
        self.assertEqual(response.status_code, 200)

    def test_delete_list_item(self):
        self.client.login(username='testuser', password='password123')
        ingredient = Ingredient.objects.create(name='sugar', quantity=1, unit='cup')
        shopping_list = ShoppingList.objects.create(user=self.user)
        list_item = ShoppingListItem.objects.create(shopping_list=shopping_list, ingredient=ingredient)
        response = self.client.post(reverse('delete_list_item', args=[list_item.id]))
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {'status': 'success', 'shopping_list_items_count': 0})

    def test_add_to_favorites(self):
        self.client.login(username='testuser', password='password123')
        response = self.client.post(reverse('add_to_favorites', args=[self.recipe.id]))
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {"success": True, "favorited": True})

    def test_list_favorites(self):
        self.client.login(username='testuser', password='password123')
        Favorite.objects.create(user=self.user, recipe=self.recipe)
        response = self.client.get(reverse('favorites'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Recipe")

    def test_your_fridge(self):
        self.client.login(username='testuser', password='password123')
        response = self.client.post(reverse('your_fridge'), {
            'ingredient_1': 'sugar',
            'ingredient_2': 'flour',
            'ingredient_3': '',
            'ingredient_4': '',
            'ingredient_5': '',
            'ingredient_6': '',
            'submitted': 'true'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Recipe")
