import sqlite3
from datetime import datetime
from app.conexion import DATABASE


def get_db_connection():
    """Establece una conexión con la base de datos SQLite."""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row 
    return conn

def save_daily_activity(user_id, activity_name, duration_minutes, calories_burned):
    """
    Guarda un registro de actividad diaria en la base de datos.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Obtener la fecha actual en formato YYYY-MM-DD (para la columna date_recorded)
    date_recorded = datetime.now().strftime('%Y-%m-%d')
    
    try:
        cursor.execute(
            "INSERT INTO daily_activities (user_id, activity_name, duration_minutes, calories_burned, date_recorded) VALUES (?, ?, ?, ?, ?)",
            (user_id, activity_name, duration_minutes, calories_burned, date_recorded)
        )
        conn.commit()
        return True # Indica que la operación fue exitosa
    except sqlite3.Error as e:
        print(f"Error al guardar actividad diaria: {e}")
        return False # Indica que la operación falló
    finally:
        conn.close()

def get_daily_activities_for_user(user_id, date=None):
    """
    Recupera las actividades diarias de un usuario en concreto, opcionalmente filtrando por fecha.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = "SELECT * FROM daily_activities WHERE user_id = ?"
    params = [user_id]
    
    if date:
        query += " AND date_recorded = ?"
        params.append(date)
        
    query += " ORDER BY timestamp DESC" # Ordena por la mas reciente primero
    
    cursor.execute(query, params)
    activities = cursor.fetchall() # Obtiene todos los resultados
    conn.close()
    return activities


def get_total_activity_minutes_today(user_id, date=None):
    """
    Devuelve la suma total de minutos de actividad realizados por el usuario en la fecha dada (por defecto, hoy).
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    if date is None:
        date = datetime.now().strftime('%Y-%m-%d')

    try:
        cursor.execute(
            "SELECT SUM(duration_minutes) AS total_minutes FROM daily_activities WHERE user_id = ? AND date_recorded = ?",
            (user_id, date)
        )
        result = cursor.fetchone()
        return result["total_minutes"] if result["total_minutes"] is not None else 0
    except sqlite3.Error as e:
        print(f"Error al obtener total de minutos: {e}")
        return 0
    finally:
        conn.close()

def get_total_calories_burned_today(user_id, date=None):
    """
    Devuelve la suma total de calorías quemadas por el usuario en actividades del día.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    if date is None:
        date = datetime.now().strftime('%Y-%m-%d')

    try:
        cursor.execute(
            "SELECT SUM(calories_burned) AS total_burned FROM daily_activities WHERE user_id = ? AND date_recorded = ?",
            (user_id, date)
        )
        result = cursor.fetchone()
        return result["total_burned"] if result["total_burned"] is not None else 0
    except sqlite3.Error as e:
        print(f"Error al obtener calorías quemadas: {e}")
        return 0
    finally:
        conn.close()


def update_activity(activity_id, user_id, activity_name, duration_minutes, calories_burned):
    """
    Actualiza una actividad existente.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            UPDATE daily_activities
            SET activity_name = ?, duration_minutes = ?, calories_burned = ?
            WHERE id = ? AND user_id = ?
            """,
            (activity_name, duration_minutes, calories_burned, activity_id, user_id)
        )
        conn.commit()
        return cursor.rowcount > 0  # True si se actualizó
    except sqlite3.Error as e:
        print(f"Error al actualizar actividad: {e}")
        return False
    finally:
        conn.close()


def delete_activity(activity_id, user_id):
    """
    Elimina una actividad de la base de datos.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "DELETE FROM daily_activities WHERE id = ? AND user_id = ?",
            (activity_id, user_id)
        )
        conn.commit()
        return cursor.rowcount > 0  # True si se eliminó
    except sqlite3.Error as e:
        print(f"Error al eliminar actividad: {e}")
        return False
    finally:
        conn.close()


