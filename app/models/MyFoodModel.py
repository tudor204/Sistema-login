# app/models/MyFoodModel.py
from datetime import datetime
from app.conexion import get_db_cursor

def _format_date_display(date_str):
    """Convierte 'YYYY-MM-DD' -> 'DD/MM/YYYY' para mostrar en UI."""
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").strftime("%d/%m/%Y")
    except Exception:
        return date_str or ""

def serialize_comida(row):
    """Convierte sqlite3.Row a dict listo para la vista y edición."""
    if row is None:
        return None
    date_iso = row["date"]
    return {
        "id": row["id"],
        "food_name": row["food_name"],
        "calories": row["calories"],
        "proteins": row["proteins"],
        "date": _format_date_display(date_iso),
        "date_iso": date_iso  # para input type="date"
    }

def get_comidas_by_user(user_id, limit=None, offset=None):
    """Obtener comidas del usuario, ya serializadas. Soporta limit/offset opcional."""
    with get_db_cursor() as cur:
        sql = """
            SELECT id, food_name, calories, proteins, date
            FROM food_entries
            WHERE user_id = ?
            ORDER BY date DESC
        """
        params = [user_id]
        if limit is not None:
            sql += " LIMIT ?"
            params.append(limit)
            if offset is not None:
                sql += " OFFSET ?"
                params.append(offset)
        cur.execute(sql, tuple(params))
        rows = cur.fetchall()
        return [serialize_comida(r) for r in rows]

def get_comida_by_id(user_id, comida_id):
    """Devuelve una comida serializada o None."""
    with get_db_cursor() as cur:
        cur.execute("""
            SELECT id, food_name, calories, proteins, date
            FROM food_entries
            WHERE user_id = ? AND id = ?
        """, (user_id, comida_id))
        row = cur.fetchone()
        return serialize_comida(row)

def delete_comida(user_id, comida_id):
    """Elimina y devuelve True si se borró una fila."""
    with get_db_cursor() as cur:
        cur.execute("DELETE FROM food_entries WHERE id = ? AND user_id = ?", (comida_id, user_id))
        return cur.rowcount > 0

def update_comida(user_id, comida_id, food_name, calories, proteins, date_iso):
    """Actualiza la fila y devuelve True si fue exitosa."""
    with get_db_cursor() as cur:
        cur.execute("""
            UPDATE food_entries
            SET food_name = ?, calories = ?, proteins = ?, date = ?
            WHERE id = ? AND user_id = ?
        """, (food_name, calories, proteins, date_iso, comida_id, user_id))
        return cur.rowcount > 0

def create_comida(user_id, food_name, calories, proteins, date_iso):
    """Crea una comida y devuelve el id insertado (o None si falló)."""
    with get_db_cursor() as cur:
        cur.execute("""
            INSERT INTO food_entries (user_id, food_name, calories, proteins, date)
            VALUES (?, ?, ?, ?, ?)
        """, (user_id, food_name, calories, proteins, date_iso))
        return getattr(cur, "lastrowid", None)
