from django.test import TestCase

# Create your tests here.
from .models import Ingredient, MenuItem, MenuItemIngredient, Order, OrderItem, Inventory

class RestaurantAppTest(TestCase):

    def setUp(self):
        # Create test ingredients
        self.ingredient1 = Ingredient.objects.create(name="Tomato", quantity_in_stock=100, cost=0.50)
        self.ingredient2 = Ingredient.objects.create(name="Cheese", quantity_in_stock=50, cost=1.00)
        self.ingredient3 = Ingredient.objects.create(name="Basil", quantity_in_stock=30, cost=0.25)

        # Create an inventory instance
        self.inventory = Inventory.objects.create()
        self.inventory.ingredients.add(self.ingredient1, self.ingredient2, self.ingredient3)

        # Create a menu item
        self.menu_item = MenuItem.objects.create(name="Margherita Pizza", price=10.00, description="Classic pizza", num_left=10)

        # Link ingredients to the menu item via MenuItemIngredient
        self.menu_item_ingredient1 = MenuItemIngredient.objects.create(menu_item=self.menu_item, ingredient=self.ingredient1, quantity_required=5)
        self.menu_item_ingredient2 = MenuItemIngredient.objects.create(menu_item=self.menu_item, ingredient=self.ingredient2, quantity_required=3)
        self.menu_item_ingredient3 = MenuItemIngredient.objects.create(menu_item=self.menu_item, ingredient=self.ingredient3, quantity_required=2)

        # Create an order
        self.order = Order.objects.create(is_complete=False, tip=2.00)

        # Create an order item with no modifications
        self.order_item = OrderItem.objects.create(order=self.order, menu_item=self.menu_item, modification='{}', modified_price=10.00)
        self.order.pretty_print_order()

    def test_order_total(self):
        """ Test that the order total is calculated correctly with tax and tip """
        total = self.order.get_total()
        expected_total = (10.00 * 1.20) + 2.00  # Item price + 20% tax + tip
        self.assertEqual(total, expected_total)

    def test_inventory_feasibility(self):
        """ Test if the inventory is feasible for a given menu item """
        result = self.inventory.is_feasible("Margherita Pizza")
        self.assertTrue(result['feasible'])

    def test_inventory_update(self):
        """ Test if the inventory updates correctly after an order """
        self.inventory.update_inventory("Margherita Pizza")
        self.ingredient1.refresh_from_db()
        self.ingredient2.refresh_from_db()
        self.ingredient3.refresh_from_db()

        self.assertEqual(self.ingredient1.quantity_in_stock, 95)  # 5 used
        self.assertEqual(self.ingredient2.quantity_in_stock, 47)  # 3 used
        self.assertEqual(self.ingredient3.quantity_in_stock, 28)  # 2 used

    def test_order_completion(self):
        """ Test that completing an order updates the inventory and marks the order as complete """
        self.order.complete_order()
        self.order.refresh_from_db()
        self.assertTrue(self.order.is_complete)

    def test_order_item_modification(self):
        """ Test that order items can be modified and the price reflects the modification """
        self.order_item.modification = '{"Tomato": 2, "Cheese": -1}'  # Add 2 tomatoes, remove 1 cheese
        self.order_item.process_modification()

        # Check the modified price
        self.assertEqual(self.order_item.modified_price, 10.50)  # Price should increase by 0.50 (2 * 0.50 - 1 * 1.00)

        # Check the pretty print functionality (no errors)
        self.order_item.pretty_print_item()

if __name__ == '__main__':
    TestCase.main()
