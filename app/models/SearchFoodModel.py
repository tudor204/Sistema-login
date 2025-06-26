from flask_login import current_user
from app.conexion import get_db_cursor

def save_food_entry(food_name, calories, proteins):
    with get_db_cursor() as cur:
        cur.execute(
            "INSERT INTO food_entries (user_id, food_name, calories, proteins) VALUES (?, ?, ?, ?)",
            (current_user.id, food_name, calories, proteins)
        )
