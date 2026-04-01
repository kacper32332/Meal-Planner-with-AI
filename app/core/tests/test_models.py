from django.test import TestCase
from django.contrib.auth.models import User
from datetime import date

# Replace 'your_app' with the actual name of your Django app
from core.models import (
    DietaryPreference, Allergy, UserProfile, Ingredient, 
    IngredientAllData, Recipe, Meal, ShoppingList, ShoppingListItem
)

class UserProfileTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testchef', password='password123')
        self.vegan_diet = DietaryPreference.objects.create(name='Vegan')
        self.peanut_allergy = Allergy.objects.create(name='Peanuts')

    def test_user_profile_creation_and_str(self):
        profile = UserProfile.objects.create(
            user=self.user,
            dietary_preference=self.vegan_diet
        )
        profile.allergies.add(self.peanut_allergy)
        
        self.assertEqual(str(profile), "testchef Profile")
        self.assertEqual(profile.dietary_preference.name, 'Vegan')
        self.assertIn(self.peanut_allergy, profile.allergies.all())


class RecipeMethodTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='recipeuser', password='password123')
        # Create a basic, uncategorized recipe
        self.recipe = Recipe.objects.create(
            name="Mystery Stew",
            description="A stew with unknown origins.",
            steps="1. Put in pot. 2. Boil.",
            created_by=self.user
        )

    def test_recipe_str(self):
        self.assertEqual(str(self.recipe), "Mystery Stew")

    def test_is_categorized_false_by_default(self):
        """Test that a new recipe without category fields returns False"""
        self.assertFalse(self.recipe.is_categorized())
        self.assertEqual(self.recipe.get_category_display(), "Not categorized")

    def test_is_categorized_true_when_fields_filled(self):
        """Test that is_categorized returns True when all 3 fields are present"""
        self.recipe.cuisine_type = 'American'
        self.recipe.difficulty = 'Easy'
        self.recipe.cooking_time = 'Under 30 mins'
        self.recipe.save()

        self.assertTrue(self.recipe.is_categorized())
        self.assertEqual(
            self.recipe.get_category_display(), 
            "American • Easy • Under 30 mins"
        )

    def test_is_categorized_partial_fields(self):
        """Test that missing even one field keeps it uncategorized"""
        self.recipe.cuisine_type = 'American'
        self.recipe.difficulty = 'Easy'
        # cooking_time is left blank intentionally
        self.recipe.save()

        self.assertFalse(self.recipe.is_categorized())


class MealFallbackTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='mealuser', password='password123')
        self.recipe = Recipe.objects.create(name="Pancakes", steps="Mix and fry.")

    def test_meal_str_with_all_data(self):
        meal = Meal.objects.create(
            user=self.user,
            recipe=self.recipe,
            date=date(2026, 4, 2),
            meal_type='breakfast'
        )
        self.assertEqual(str(meal), "Breakfast on 2026-04-02 - Pancakes")

    def test_meal_str_missing_optional_data(self):
        """Test the fallback strings in the Meal __str__ method"""
        meal = Meal.objects.create(
            user=self.user,
            recipe=self.recipe
            # date and meal_type left blank
        )
        self.assertEqual(str(meal), "Meal on No date - Pancakes")


class ShoppingListThroughModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='shopper', password='password123')
        self.tomato = IngredientAllData.objects.create(name="Tomato")
        self.onion = IngredientAllData.objects.create(name="Onion")

    def test_shopping_list_item_creation(self):
        shopping_list = ShoppingList.objects.create(user=self.user)
        
        # Create the through model instances
        item1 = ShoppingListItem.objects.create(
            shopping_list=shopping_list,
            ingredient=self.tomato,
            quantity="3 whole"
        )
        item2 = ShoppingListItem.objects.create(
            shopping_list=shopping_list,
            ingredient=self.onion,
            quantity="1 large"
        )

        # Test the string representation of the through model
        self.assertEqual(str(item1), "3 whole Tomato")
        
        # Test that the ManyToMany relationship works backwards
        self.assertEqual(shopping_list.items.count(), 2)
        self.assertIn(self.tomato, shopping_list.items.all())