from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from unittest.mock import patch
from .models import Recipe, Ingredient, ShoppingList, ShoppingListItem
from .forms import RecipeForm

class RecipeAppTests(TestCase):
    def setUp(self):
        # Create a user for authentication tests
        self.user = User.objects.create_user(username='testuser', password='12345')

    def test_register_POST_success(self):
        response = self.client.post(reverse('register'), {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'password123',
            'confirmation': 'password123'
        })
        self.assertEqual(response.status_code, 302)  # Redirect to index
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_register_POST_password_mismatch(self):
        response = self.client.post(reverse('register'), {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'password123',
            'confirmation': 'password321'
        })
        self.assertIn("Passwords must match.", response.content.decode())

    def test_login_POST_success(self):
        self.client.login(username='testuser', password='12345')
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': '12345'
        })
        self.assertEqual(response.status_code, 302)

    def test_login_POST_invalid_credentials(self):
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'wrong'
        })
        self.assertIn("Invalid username and/or password.", response.content.decode())

    def test_logout_view(self):
        self.client.login(username='testuser', password='12345')
        response = self.client.get(reverse('logout'))
        self.assertEqual(response.status_code, 302)  # Redirect to index

    @patch('recepies.views.RecipeForm')
    def test_recipe_add_POST_valid(self, mock_form):
        mock_form.return_value.is_valid.return_value = True
        mock_form.return_value.save.return_value = Recipe(id=1)  # Assuming save is overridden
        self.client.login(username='testuser', password='12345')
        response = self.client.post(reverse('index'), {})
        self.assertEqual(response.status_code, 200)  # Redirect to index

    def test_recipe_add_POST_invalid(self):
        self.client.login(username='testuser', password='12345')
        response = self.client.post(reverse('recipe_add'), {})
        self.assertEqual(response.status_code, 200)  # Stay on form
        self.assertIn("form", response.context)

    @patch('recepies.views.Recipe.objects.get')
    @patch('recepies.views.ShoppingList.objects.get_or_create')
    @patch('recepies.views.ShoppingListItem.objects.create')
    def test_generate_shopping_list(self, mock_create, mock_get_or_create, mock_get):
        mock_get.return_value = Recipe(id=1)
        mock_get_or_create.return_value = (ShoppingList(id=1), True)
        self.client.login(username='testuser', password='12345')
        response = self.client.get(reverse('generate_shopping_list', args=[1]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'status': 'success', 'shopping_list_id': 1})
