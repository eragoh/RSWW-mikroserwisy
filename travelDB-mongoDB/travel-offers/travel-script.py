import json
import random

def distribute_children(total_children):
    # Initialize counts for different age groups
    children_under_3 = 0
    children_under_10 = 0
    children_under_18 = 0

    # Randomly distribute children among the categories
    for _ in range(total_children):
        age = random.randint(0, 17)  # Generate a random age between 0 and 17

        if age < 3:
            children_under_3 += 1
        elif age < 10:
            children_under_10 += 1
        else:
            children_under_18 += 1

    return children_under_3, children_under_10, children_under_18


def add_categories(file_path):
    # Read the JSON data
    with open(file_path, 'r') as f:
        data = json.load(f)

    # Process each hotel entry
    for hotel in data:
        total_children = hotel.get("children", 0)

        # Randomly distribute children
        children_under_3, children_under_10, children_under_18 = distribute_children(total_children)

        # Add the new categories
        hotel['children_under_3'] = children_under_3
        hotel['children_under_10'] = children_under_10
        hotel['children_under_18'] = children_under_18

    # Save the updated data back to a JSON file
    with open('updated_travel-offers.json', 'w') as f:
        json.dump(data, f, indent=4)

# Example usage
add_categories('travel-offers.json')
