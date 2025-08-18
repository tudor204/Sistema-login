from app.conexion import get_db_cursor

def get_comidas_by_user(user_id):
    """Obtener todas las comidas de un usuario ordenadas por fecha."""
    with get_db_cursor() as cur:
        cur.execute("""
            SELECT id, food_name, calories, proteins, date
            FROM food_entries
            WHERE user_id = ?
            ORDER BY date DESC
        """, (user_id,))
        return cur.fetchall()

def delete_comida(user_id, comida_id):
    """Eliminar una comida de un usuario específico."""
    with get_db_cursor() as cur:
        cur.execute(
            "DELETE FROM food_entries WHERE id = ? AND user_id = ?", 
            (comida_id, user_id)
        )
