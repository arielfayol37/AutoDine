from django.db import models
from django.db import models
import os
from django.conf import settings

# from decimal import Decimal


class Ingredient(models.Model):
    """Base constituent of food items"""
    name = models.CharField(max_length=100)
    quantity_in_stock = models.IntegerField(help_text="Quantity available in stock")
    cost = models.FloatField(default=0.0, null=False, blank=False)

    def __str__(self):
        return self.name

class MenuItem(models.Model):
    """Represents the default menu items and their usual ingredients"""
    name = models.CharField(max_length=100)
    price = models.FloatField(null=False, blank=False)
    description = models.TextField()
    ingredients = models.ManyToManyField(Ingredient, through='MenuItemIngredient')

    def __str__(self):
        return self.name

    def get_ingredients(self):
        """Returns the ingredients and their required quantities for the menu item."""
        ingredients_info = {}
        menu_item_ingredients = MenuItemIngredient.objects.filter(menu_item=self)
        for item_ingredient in menu_item_ingredients:
            ingredients_info[item_ingredient.ingredient.name] = item_ingredient.quantity_required
        return ingredients_info

    @property
    def image_url(self):
        """Dynamically generates the URL for the image based on the menu item name."""
        image_name = f"{self.name.lower().replace(' ', '_')}.jpg"  # Generate image name, e.g., "egg_sandwich.jpg"
        image_path = os.path.join("images", "menu_items", image_name)  # Assuming images are stored in 'images/menu_items/'
        # static_image_path = os.path.join(settings.STATIC_ROOT, image_path)  # Check in STATIC_ROOT for the file
        target_url = os.path.join(settings.STATIC_URL, image_path)  # URL to return if the image exists
        return target_url
class MenuItemIngredient(models.Model):
    """This model represents the quantity of each ingredient needed for a MenuItem."""
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    quantity_required = models.IntegerField(help_text="Amount of this ingredient needed for the item")

    def __str__(self):
        return f"{self.quantity_required} of {self.ingredient.name} for {self.menu_item.name}"

class Order(models.Model):
    """Represents a customer order."""
    created_at = models.DateTimeField(auto_now_add=True)
    is_complete = models.BooleanField(default=False)
    tip = models.FloatField(default=0.00, help_text="Tip amount")
    # MenuItems with their specific modifications
    menu_items = models.ManyToManyField(MenuItem, through='OrderItem')

    def __str__(self):
        return f"Order #{self.id} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"

    def get_total(self):
        """ Sums all the items on the order and adds a 20% tax fee, plus tip """
        total = sum(order_item.get_modified_price() for order_item in self.orderitem_set.all())
        total_with_tax = total * 1.20  # Adding 20% tax
        return total_with_tax + self.tip

    def pretty_print_order(self):
        """ Nicely prints the order details with item names, prices, and ingredient modifications. """
        order_details = f"Order #{self.id}:\n"
        for order_item in self.orderitem_set.all():
            # order_item.process_modification()
            order_details += order_item.pretty_print_item()
        order_details += f"Tip: ${self.tip}\n"
        order_details += f"Total (including 20% tax): ${round(self.get_total(), 2)}\n"
        return order_details

    def complete_order(self):
        """
        Marks the order as complete and updates the inventory by deducting the used ingredients.
        """
        for order_item in self.orderitem_set.all():
            order_item.update_inventory()  # Deduct ingredients from inventory
        self.is_complete = True
        self.save()

class OrderItem(models.Model):
    """
    Represents a specific item in an order, allowing for ingredient modifications.
    Stores modifications for the MenuItem in an Order, such as extra or fewer ingredients.
    """
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    modification = models.TextField(null=True, blank=True)
    modified_price = models.FloatField(blank=True, null=True)
    order_print = models.TextField(null=True, blank=True)
    actual_ingredients = models.TextField(null=True, blank=True)

    def process_modification(self):
        actual_ingredients = {}
        marginal_cost = 0.0
        addition, removed, exact = {}, {}, {}
        modification = eval(self.modification)
        # Get all ingredients needed for this menu item
        ingredients_required = MenuItemIngredient.objects.filter(menu_item=self.menu_item)
        # Check if the inventory has enough of each ingredient
        for item_ingredient in ingredients_required:
            ingredient = item_ingredient.ingredient
            required_quantity = item_ingredient.quantity_required
            # Include any additional ingredients passed in
            if ingredient.name in modification:
                val = modification[ingredient.name]
                if type(val) == int:
                    required_quantity += val
                    if val < 0:
                        removed[item_ingredient.ingredient.name] = abs(val)
                    elif val > 0:
                        addition[item_ingredient.ingredient.name] = abs(val)
                elif type(val) == str:
                    required_quantity = int(val[1:-1])
                else:
                    raise ValueError("Unexpected input. We expect either an integer or something like -4- to\
                                        set the exact number for this ingredient")
            actual_ingredients[ingredient.name] = required_quantity
            marginal_cost += (required_quantity - item_ingredient.quantity_required ) * (ingredient.cost)
        
        self.modified_price = self.menu_item.price + marginal_cost
        self.set_order_print(addition, removed, exact)
        self.actual_ingredients = str(actual_ingredients)
        # print("self.actual: ", self.actual_ingredients)
        self.save()

    def get_modified_price(self):
        """Calculate the price of the item based on any modifications (e.g., extra cheese might cost more)."""
        return self.modified_price if self.modified_price else self.menu_item.price

    def set_order_print(self, addition, removed, exact):
        """Sets the order print"""
        details = f"{self.menu_item.name}: ${self.get_modified_price()}\n"
        for item, val in exact:
            details += f"  exactly {val} of {item}\n"
        for item, val in addition.items():
            details += f"  +{val} of {item}\n"
        for item, val in removed.items():
            details += f"  -{val} of {item}\n"
        self.order_print = details
        self.save()

    def pretty_print_item(self):
        """Prints the item with modifications (additional or removed ingredients)."""
        return self.order_print

    def update_inventory(self):
        """
        Deducts the required ingredients for this order item from the inventory.
        Takes into account additional or removed ingredients.
        """
        # Deduct default ingredients for the menu item
        # print(self.actual_ingredients)
        actual_ingredients = eval(self.actual_ingredients)
        for ingredient_name, val in actual_ingredients.items():
            ingredient = Ingredient.objects.get(name=ingredient_name)
            ingredient.quantity_in_stock -= max(0, val)
            ingredient.save()
        

class Inventory(models.Model):
    ingredients = models.ManyToManyField(Ingredient)

    def is_feasible(self, item_name, additional_ingredients={}):
        """
        Takes in the name of the item to make, and a dictionary of additional ingredients to add or subtract 
        (with their count), and determines if it is possible.
        
        Returns a dictionary with 'feasible': True/False, and in case of False, includes missing ingredients.
        """
        response = {
            'feasible': True,
            'missing_ingredients': []
        }

        try:
            marginal_cost = 0
            stop = False
            # Get the menu item
            menu_item = MenuItem.objects.get(name=item_name)
            # Get all ingredients needed for this menu item
            ingredients_required = MenuItemIngredient.objects.filter(menu_item=menu_item)

            # Check if the inventory has enough of each ingredient
            for item_ingredient in ingredients_required:
                ingredient = item_ingredient.ingredient
                required_quantity = item_ingredient.quantity_required

                # Include any additional ingredients passed in
                if ingredient.name in additional_ingredients:
                    val = additional_ingredients[ingredient.name]
                    if type(val) == int:
                        required_quantity += val
                    elif type(val) == str:
                        required_quantity = int(val[1:-1])
                    else:
                        raise ValueError("Unexpected input. We expect either an integer or something like -4- to\
                                          set the exact number for this ingredient")
                # print(f"ingredient: {ingredient.name}, quantity: {required_quantity}")
                # Check if inventory has enough stock
                if ingredient.quantity_in_stock < required_quantity:
                    response['feasible'] = False
                    response['missing_ingredients'].append({
                        'ingredient': ingredient.name,
                        'required': required_quantity,
                        'available': ingredient.quantity_in_stock
                    })
                    total, stop = 0, True
                if not stop:
                    marginal_cost += (required_quantity - item_ingredient.quantity_required) * ingredient.cost
            if not stop: response["total_cost"] = round(menu_item.price + marginal_cost, 2)
            return response

        except MenuItem.DoesNotExist:
            return {'feasible': False, 'error': f"'{item_name}' is not on the menu."}


    def update_inventory(self, item_name, additional_ingredients={}):
        """
        Updates the inventory by taking an item_name and decrementing the ingredients that have been used.
        It also handles additional ingredients (if passed) that should be added or subtracted.
        """
        if self.is_feasible(item_name, additional_ingredients):
            # Get the menu item
            menu_item = MenuItem.objects.get(name=item_name)

            # Get all ingredients needed for this menu item
            ingredients_required = MenuItemIngredient.objects.filter(menu_item=menu_item)

            # Decrement each ingredient in stock by the required quantity
            for item_ingredient in ingredients_required:
                ingredient = item_ingredient.ingredient
                required_quantity = item_ingredient.quantity_required

                # Include any additional ingredients passed in
                if ingredient.name in additional_ingredients: # POTENTIAL BUG HERE WE SET OPTION
                    required_quantity += additional_ingredients[ingredient.name]

                # Update ingredient stock
                ingredient.quantity_in_stock -= required_quantity
                ingredient.save()
            return True
        return False
