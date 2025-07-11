import sqlite3
from datetime import datetime
from app.conexion import DATABASE

# Define la ruta de tu base de datos


def get_db_connection():
    """Establece una conexión con la base de datos SQLite."""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row # Permite acceder a las columnas por nombre (ej. row['id'])
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
    Recupera las actividades diarias de un usuario, opcionalmente filtrando por fecha.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = "SELECT * FROM daily_activities WHERE user_id = ?"
    params = [user_id]
    
    if date:
        query += " AND date_recorded = ?"
        params.append(date)
        
    query += " ORDER BY timestamp DESC" # Ordena por la más reciente primero
    
    cursor.execute(query, params)
    activities = cursor.fetchall() # Obtiene todos los resultados
    conn.close()
    return activities