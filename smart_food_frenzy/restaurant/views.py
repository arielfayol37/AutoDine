from django.shortcuts import render
import traceback

# Create your views here.

from django.http import JsonResponse, StreamingHttpResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt  # Import csrf_exempt decorator
from .models import Inventory, MenuItem, OrderItem, Order
import json
import time

# Dashboard info structure to store changes
dashboard_info = {
    "add_to_db": [],
    "remove_from_db": [],
    "previous items": set(),
    "total": 0.0
}

# Update dashboard info based on items and their feasibility
def update_dashboard(items, feasibility, total):
    dashboard_info
    items_keys = set(items.keys())
    
    # Add new items to the dashboard info
    for item in items_keys:
        if item not in dashboard_info["previous items"]:
            dashboard_info["add_to_db"].append({"name": item, "request": items[item], "feasibility": feasibility.get(item, "unknown")})
    
    # Remove items that are no longer in the current items set
    for prev_item in dashboard_info["previous items"]:
        if prev_item not in items_keys:
            dashboard_info["remove_from_db"].append({"name": prev_item})
    
    # Update the previous items set
    dashboard_info['previous items'] = items_keys
    dashboard_info["total"] = total

def event_stream():
    while True:
        time.sleep(1)

        # Convert the 'previous items' set to a list for JSON serialization
        dashboard_info_copy = dashboard_info.copy()  # Create a copy to avoid modifying the original
        dashboard_info_copy['previous items'] = list(dashboard_info_copy['previous items'])

        # Convert the dashboard_info to JSON and stream it
        dashboard_json = json.dumps(dashboard_info_copy)
        yield f"data: {dashboard_json}\n\n"

        # Clear the add/remove lists after streaming the data
        dashboard_info["add_to_db"].clear()
        dashboard_info["remove_from_db"].clear()


# SSE view to stream data to the client
def sse_view(request):
    return StreamingHttpResponse(event_stream(), content_type='text/event-stream')

def menu_view(request):
    menu_items = MenuItem.objects.all()  # Fetch all menu items
    return render(request, 'restaurant/menu_items.html', {'menu_items': menu_items})

@csrf_exempt  # Disable CSRF protection for this view
@require_POST
def check_feasible_items(request):
    """
    View to check the feasibility of menu items based on the current inventory.
    It expects a JSON payload with a dictionary where the keys are menu item names and the values are 
    dictionaries of additional ingredients (or empty if none).
    
    Example input:
    {
        "Burger": {"Cheese": 1, "Tomato": "-4-"},   # Extra 1 cheese on a burger, Exactly 4 Tomatoes
        "Fries": {}                # Standard fries
        "Biryani":{"Rice": 3, "Chicken": 2} # Extra 3 bowls of rice, Extra 2 chickens
    }
    
    Example output:
    {
        "Burger": {"feasible": False, "missing_ingredients": [{"ingredient": "Cheese", "required": 2, "available": 1}]},
        "Fries": {"feasible": True}
        "Biryani":{"feasible": True} 
    }
    """
    # Ensure the data is in JSON format
    try:
        json_req = json.loads(request.body)
        items = json_req['items']
        if not items:
            return JsonResponse({'error': 'Invalid data format or missing items key.'}, status=400)

        # Initialize response dictionary
        feasibility = {}

        # Get the current inventory instance (assuming you have only one inventory object)
        inventory = Inventory.objects.first()
        total_order_cost, stop = 0, False
        # Loop through each menu item in the input dictionary
        for item_name, additional_ingredients in items.items():
            # Check if the item is feasible in the inventory
            feasibility[item_name] = inventory.is_feasible(item_name, additional_ingredients)
            if "total_cost" not in feasibility[item_name]:
                stop = True 
                total_order_cost = 0
            elif not stop:
                total_order_cost += feasibility[item_name]["total_cost"]

        update_dashboard(items, feasibility, total_order_cost * 1.20) # 1.20 for taxes
        # Return the feasibility result as JSON
        return JsonResponse(feasibility, status=200)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt  # Disable CSRF protection for this view
@require_POST
def order_items(request):
    """
    View to place an order based on the current inventory.
    It expects a JSON payload similar to the check_feasible_items view, where the keys are menu item names
    and the values are dictionaries of additional ingredients (or empty if none).
    
    Example input:
    {
        "Burger": {"Cheese": 1, "Tomato": "-4-"},   # Extra 1 cheese on a burger, Exactly 4 Tomatoes
        "Fries": {},                # Standard fries
        "Biryani": {"Rice": 3, "Chicken": 2}  # Extra 3 bowls of rice, Extra 2 chickens
    }
    
    This view creates a new order and updates the inventory accordingly.
    """
    try:
        # Parse the request body
        json_req = json.loads(request.body)
        items = json_req.get('items', {})
        tip = json_req.get("tip", 0.0)

        if not items:
            return JsonResponse({'error': 'No items provided.'}, status=400)

        # Initialize the order
        order = Order.objects.create(tip=tip)

        # Get the current inventory instance (assuming only one inventory object)
        inventory = Inventory.objects.first()

        # Loop through each menu item in the request
        for item_name, additional_ingredients in items.items():
            # Fetch the menu item by name
            menu_item = MenuItem.objects.get(name=item_name)

            # Create a new OrderItem for this menu item
            order_item = OrderItem.objects.create(
                order=order,
                menu_item=menu_item,
                # modification=json.dumps(additional_ingredients),  # Store the modification as JSON
                modification = str(additional_ingredients)
            )

            # Process any modifications to calculate the correct ingredient quantities
            order_item.process_modification()

            # Update the inventory based on the required ingredients for this item
            # order_item.update_inventory()

        # Mark the order as complete
        order.complete_order()
        dashboard_info["add_to_db"].clear()
        dashboard_info["remove_from_db"].clear()
        dashboard_info["previous items"].clear()
        dashboard_info["total"] = 0.0
        # Return success response
        return JsonResponse({
            'status': 'success',
            'message': f'Order #{order.id} created and processed successfully.',
            'order_id': order.id, 
            "pretty_print":order.pretty_print_order(),
        }, status=200)

    except MenuItem.DoesNotExist:
        return JsonResponse({'error': f"Menu item '{item_name}' does not exist."}, status=404)
    
    except Exception as e:
        # Capture the full traceback and send it in the response
        error_trace = traceback.format_exc()
        return JsonResponse({
            'error': str(e),
            'traceback': error_trace
        }, status=500)


