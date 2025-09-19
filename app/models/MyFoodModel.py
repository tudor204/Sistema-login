from datetime import datetime, date
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
        "fats": row["fats"],
        "carbs": row["carbs"],
        "date": _format_date_display(date_iso),
        "date_iso": date_iso  # para input type="date"
    }

def get_comidas_by_user(user_id, limit=None, offset=None):
    """Obtener todas las comidas del usuario (histórico completo)."""
    with get_db_cursor() as cur:
        sql = """
            SELECT id, food_name, calories, proteins, fats, carbs, date
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

def get_totales_diarios(user_id):
    """Devuelve los totales (calorías y proteínas) solo para el día actual."""
    with get_db_cursor() as cur:
        cur.execute("""
            SELECT 
                COALESCE(SUM(calories), 0) AS total_calorias,
                COALESCE(SUM(proteins), 0) AS total_proteinas
            FROM food_entries
            WHERE user_id = ? AND date = ?
        """, (user_id, date.today().isoformat()))
        row = cur.fetchone()
        return {
            "total_calorias": int(row["total_calorias"] or 0),
            "total_proteinas": int(row["total_proteinas"] or 0)
        }

def get_comida_by_id(user_id, comida_id):
    """Devuelve una comida serializada o None."""
    with get_db_cursor() as cur:
        cur.execute("""
            SELECT id, food_name, calories, proteins, fats, carbs, date
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

def update_comida(user_id, comida_id, food_name, calories, proteins, fats, carbs, date_iso):
    """Actualiza la fila y devuelve True si fue exitosa."""
    with get_db_cursor() as cur:
        cur.execute("""
            UPDATE food_entries
            SET food_name = ?, calories = ?, proteins = ?, fats = ?, carbs = ?, date = ?
            WHERE id = ? AND user_id = ?
        """, (food_name, calories, proteins, fats, carbs, date_iso, comida_id, user_id))
        return cur.rowcount > 0

def create_comida(user_id, food_name, calories, proteins, fats, carbs, date_iso):
    """Crea una comida y devuelve el id insertado (o None si falló)."""
    with get_db_cursor() as cur:
        cur.execute("""
            INSERT INTO food_entries (user_id, food_name, calories, proteins, fats, carbs, date)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (user_id, food_name, calories, proteins, fats, carbs, date_iso))
        return getattr(cur, "lastrowid", None)
