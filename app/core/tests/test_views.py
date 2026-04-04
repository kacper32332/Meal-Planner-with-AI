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
            "password2": "securepassword123",
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

class MultipleAllergiesEdgeCaseTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='allergy_user', password='password')
        self.profile = UserProfile.objects.create(user=self.user)
        self.client.force_authenticate(user=self.user)

        self.peanut_allergy = Allergy.objects.create(name="Peanuts")
        self.dairy_allergy = Allergy.objects.create(name="Dairy")
        self.profile.allergies.add(self.peanut_allergy, self.dairy_allergy)

        self.tomato = IngredientAllData.objects.create(name="Tomato")
        self.pasta = IngredientAllData.objects.create(name="Pasta")
        self.peanut_butter = IngredientAllData.objects.create(name="Peanut Butter")
        self.milk = IngredientAllData.objects.create(name="Milk")

        Ingredient.objects.create(user=self.user, name="Tomato", is_available=True)
        Ingredient.objects.create(user=self.user, name="Pasta", is_available=True)

        self.safe_recipe = Recipe.objects.create(name="Tomato Pasta", steps="Boil and mix.")
        self.safe_recipe.ingredients.add(self.tomato, self.pasta)

        self.peanut_recipe = Recipe.objects.create(name="Peanut Pasta", steps="Mix PB and pasta.")
        self.peanut_recipe.ingredients.add(self.pasta, self.tomato, self.peanut_butter)
        self.peanut_recipe.contains_allergens.add(self.peanut_allergy)

        self.dairy_recipe = Recipe.objects.create(name="Creamy Tomato", steps="Mix milk and tomato.")
        self.dairy_recipe.ingredients.add(self.tomato, self.pasta, self.milk)
        self.dairy_recipe.contains_allergens.add(self.dairy_allergy)

        self.sneaky_recipe = Recipe.objects.create(name="Cross Contaminated Pasta", steps="Cook.")
        self.sneaky_recipe.ingredients.add(self.tomato, self.pasta)
        self.sneaky_recipe.contains_allergens.add(self.dairy_allergy)

    def test_recipe_search_blocks_all_allergens(self):
        """
        Test that RecipeSearchView excludes recipes containing ANY of the user's allergens,
        even if the user searches for ingredients that are present in those bad recipes.
        """
        url = reverse('recipe-search')
        
        data = {"ingredients": ["Pasta", "Tomato"]}
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.assertEqual(response.data['total_count'], 1)
        self.assertEqual(response.data['results'][0]['name'], "Tomato Pasta")
        
        result_names = [recipe['name'] for recipe in response.data['results']]
        self.assertNotIn("Peanut Pasta", result_names)
        self.assertNotIn("Creamy Tomato", result_names)

    def test_matching_recipes_blocks_sneaky_allergens(self):
        """
        Test that the matching_recipes endpoint correctly applies the 'contains_allergens' 
        exclusion, even if the recipe's ingredient list looks completely safe.
        """
        url = reverse('matching-recipes')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], "Tomato Pasta")