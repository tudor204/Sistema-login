from app.conexion import get_db_cursor
import datetime
import locale

# Establecemos el locale en español para que strftime devuelva días en español
try:
    locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')
except locale.Error:
    # En Windows o si no está instalado 'es_ES.UTF-8', puede fallar.
    # En ese caso puedes instalarlo o usar otro método.
    pass

def obtener_dias_registrados(user_id):
    with get_db_cursor() as cur:
        cur.execute("""
            SELECT DISTINCT date(date) as dia
            FROM food_entries
            WHERE user_id = ?
            ORDER BY dia DESC
        """, (user_id,))
        filas = cur.fetchall()
    
    resultado = []
    for row in filas:
        fecha_str = row['dia']
        fecha_obj = datetime.datetime.strptime(fecha_str, '%Y-%m-%d').date()
        dia_semana = fecha_obj.strftime('%a')  # abreviatura día de la semana en español si locale está bien
        # Para asegurar abreviaturas tipo 'Lun', 'Mar' puedes hacer replace si hace falta:
        # dia_semana = dia_semana.capitalize()
        resultado.append({'fecha': fecha_str, 'dia_semana': dia_semana})
    return resultado

def obtener_resumen_dia(user_id, fecha):
    with get_db_cursor() as cur:
        # Alimentos y calorías
        cur.execute("""
            SELECT food_name, calories, proteins, fats, carbs
            FROM food_entries
            WHERE user_id = ? AND date(date) = ?
        """, (user_id, fecha))
        alimentos = [dict(row) for row in cur.fetchall()]

        # Actividades
        cur.execute("""
            SELECT activity_name, duration_minutes, calories_burned
            FROM daily_activities
            WHERE user_id = ? AND date(date_recorded) = ?
        """, (user_id, fecha))
        actividades = [dict(row) for row in cur.fetchall()]

        return {
            'alimentos': alimentos,
            'actividades': actividades
        }
