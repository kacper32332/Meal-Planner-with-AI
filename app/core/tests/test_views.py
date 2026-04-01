from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from core.models import Ingredient, IngredientAllData, Recipe, UserProfile, Allergy

class RecipeAPITests(APITestCase):
    def setUp(self):
        # Create user and profile
        self.user = User.objects.create_user(username='chef_test', password='password123')
        self.profile = UserProfile.objects.create(user=self.user)
        self.client.force_authenticate(user=self.user)
        
        # Setup data
        self.tomato = IngredientAllData.objects.create(name="Tomato")
        self.salt = IngredientAllData.objects.create(name="Salt")
        
        self.recipe = Recipe.objects.create(
            name="Salted Tomato", 
            steps="Put salt on tomato."
        )
        self.recipe.ingredients.add(self.tomato, self.salt)

    def test_recipe_search_view(self):
        """Tests the RecipeSearchView (APIView)"""
        url = reverse('recipe-search')
        data = {"ingredients": ["Tomato", "Salt"]}
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Check if the result count is correct
        self.assertEqual(response.data['total_count'], 1)
        self.assertEqual(response.data['results'][0]['name'], "Salted Tomato")

    def test_categorize_action(self):
        """Tests the @action 'categorize' inside RecipeViewSet"""
        # Router name + action name
        url = reverse('recipe-categorize', kwargs={'pk': self.recipe.pk})
        data = {
            "cuisine_type": "Other",
            "difficulty": "Easy",
            "cooking_time": "Under 30 mins"
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.recipe.refresh_from_db()
        self.assertEqual(self.recipe.cuisine_type, "Other")

class UserManagementTests(APITestCase):
    def test_registration(self):
        """Tests CreateUserView"""
        url = reverse('register')
        data = {
            "username": "newuser",
            "password": "securepassword123",
            "email": "new@example.com"
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username="newuser").exists())

    def test_current_user_profile(self):
        """Tests CurrentUserView retrieval"""
        user = User.objects.create_user(username='profileuser', password='password')
        self.client.force_authenticate(user=user)
        
        url = reverse('current-user')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'profileuser')

class IngredientTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='fridge_user', password='password')
        self.client.force_authenticate(user=self.user)
        self.global_ing = IngredientAllData.objects.create(name="Apple")

    def test_add_from_global_action(self):
        """Tests the @action 'add_from_global' in IngredientViewSet"""
        url = reverse('ingredient-add-from-global')
        data = {"name": "Apple", "quantity": "2"}
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(Ingredient.objects.filter(user=self.user, name="Apple").exists())