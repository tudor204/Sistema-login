from flask_login import current_user
from app.conexion import get_db_cursor

def calculate_macros_for_quantity(calories_per_100g, proteins_per_100g, quantity_g):
    """Calcula las calorías y proteínas ajustadas a la cantidad indicada (en gramos)."""
    factor = quantity_g / 100
    calories = calories_per_100g * factor
    proteins = proteins_per_100g * factor
    return round(calories, 2), round(proteins, 2)

def save_food_entry(food_name, calories, proteins, fats=0, carbs=0):
    """Guarda la entrada de comida con todos los macros."""
    with get_db_cursor() as cur:
        cur.execute(
            """
            INSERT INTO food_entries (user_id, food_name, calories, proteins, fats, carbs)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (current_user.id, food_name, calories, proteins, fats, carbs)
        )
