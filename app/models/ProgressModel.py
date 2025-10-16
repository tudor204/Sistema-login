from app.conexion import get_db_cursor
import datetime
import locale
from app.models.SettingsModel import get_user_goals 
# Establecemos el locale en español para que strftime devuelva días en español
# Nota: La dependencia de locale es mejor evitarla si es posible, 
# pero se mantiene tu estructura original. Se recomienda usar la librería 
# babel o un mapeo manual para mayor portabilidad.
try:
    locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')
except locale.Error:
    # Intento para sistemas que usan otro formato (e.g., Mac/Linux)
    try:
        locale.setlocale(locale.LC_TIME, 'es_ES')
    except:
        pass # Fallback

def obtener_dias_registrados(user_id):
    """Obtiene una lista de todos los días con registros del usuario."""
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
        # %a: Abreviatura del día de la semana según el locale
        dia_semana_abr = fecha_obj.strftime('%a').capitalize().replace('.', '') 
        
        # Mapeo manual para asegurar abreviaturas consistentes si locale falla
        # Puedes añadir más aquí si es necesario
        mapeo = {
            'Mon': 'Lun', 'Tue': 'Mar', 'Wed': 'Mié', 'Thu': 'Jue', 
            'Fri': 'Vie', 'Sat': 'Sáb', 'Sun': 'Dom'
        }
        
        # Si la abreviatura no está en el mapa, intentamos la versión en español si se estableció el locale
        dia_semana_final = mapeo.get(dia_semana_abr, dia_semana_abr)

        resultado.append({
            'fecha': fecha_str, 
            'dia_semana': dia_semana_final
        })
    return resultado

def obtener_resumen_dia(user_id, fecha):
    """Obtiene el detalle de alimentos, actividades, y totales de macros/calorías para un día específico."""
    try:
        fecha_obj = datetime.datetime.strptime(fecha, '%Y-%m-%d').date()
        fecha_str = fecha_obj.isoformat()
    except ValueError:
        fecha_str = datetime.date.today().isoformat()

    with get_db_cursor() as cur:
        # --- Alimentos y macros detallados ---
        cur.execute("""
            SELECT food_name as name, calories, proteins, fats, carbs
            FROM food_entries
            WHERE user_id = ? AND date(date) = ?
        """, (user_id, fecha_str))
        alimentos = [dict(row) for row in cur.fetchall()]

        # --- Totales de alimentos para el dashboard del día ---
        cur.execute("""
            SELECT 
                COALESCE(SUM(calories), 0) AS total_calorias_in,
                COALESCE(SUM(proteins), 0) AS total_proteinas,
                COALESCE(SUM(fats), 0) AS total_grasas,
                COALESCE(SUM(carbs), 0) AS total_carbohidratos
            FROM food_entries
            WHERE user_id = ? AND date(date) = ?
        """, (user_id, fecha_str))
        totales_comida = dict(cur.fetchone()) or {'total_calorias_in': 0, 'total_proteinas': 0, 'total_grasas': 0, 'total_carbohidratos': 0}


        # --- Actividades y calorías quemadas ---
        cur.execute("""
            SELECT activity_name, duration_minutes, calories_burned
            FROM daily_activities
            WHERE user_id = ? AND date(date_recorded) = ?
        """, (user_id, fecha_str))
        actividades = [dict(row) for row in cur.fetchall()]

        # --- Total de calorías quemadas ---
        total_quemadas = sum(act['calories_burned'] for act in actividades)
        
        # --- Cálculo de Calorías Netas ---
        total_calorias_in = totales_comida['total_calorias_in']
        calorias_netas = total_calorias_in - total_quemadas

        return {
            'alimentos': alimentos,
            'actividades': actividades,
            'totales': {
                'total_calorias_in': total_calorias_in,
                'total_quemadas': total_quemadas,
                'calorias_netas': calorias_netas, # Métrica clave
                'total_proteinas': totales_comida['total_proteinas'],
                'total_grasas': totales_comida['total_grasas'],
                'total_carbohidratos': totales_comida['total_carbohidratos'],
            }
        }

def obtener_datos_calorias_7dias(user_id, fecha_fin):
    """Obtiene datos de calorías por día para el gráfico de 7 días."""
    with get_db_cursor() as cur:
        cur.execute("""
            SELECT date(date) AS dia, SUM(calories) AS total_calorias
            FROM food_entries
            WHERE user_id = ? AND date BETWEEN date(?, '-6 days') AND ?
            GROUP BY dia
            ORDER BY dia
        """, (user_id, fecha_fin, fecha_fin))
        return [dict(row) for row in (cur.fetchall() or [])]

def obtener_macros_totales_7dias(user_id, fecha_fin):
    """Obtiene el total de macros sumados durante 7 días."""
    with get_db_cursor() as cur:
        cur.execute("""
            SELECT 
                COALESCE(SUM(proteins), 0) AS proteinas, 
                COALESCE(SUM(fats), 0) AS grasas, 
                COALESCE(SUM(carbs), 0) AS carbohidratos
            FROM food_entries
            WHERE user_id = ? AND date BETWEEN date(?, '-6 days') AND ?
        """, (user_id, fecha_fin, fecha_fin))
        row = cur.fetchone()
        return dict(row) if row else {'proteinas': 0, 'grasas': 0, 'carbohidratos': 0}

def obtener_metas_nutricionales(user_id):
    """
    Obtiene las metas nutricionales diarias del usuario llamando a la función
    real de acceso a datos, y las mapea al formato necesario.
    """
    # 1. Obtenemos las metas reales del usuario (o las por defecto)
    # Esta función se encarga de la conexión a DB, la consulta y los defaults.
    goals_data = get_user_goals(user_id) 

    # 2. Mapeamos los campos al formato simple que usa el controlador y la vista
    # Utilizamos .get() para seguridad, aunque ya deberíamos tener defaults.
    return {
        'calorias': goals_data.get('daily_calories', 2000), # 2000 kcal default si falla
        'proteinas': goals_data.get('daily_proteins', 150), # 150g default si falla
        'grasas': goals_data.get('daily_fats', 60),         # 60g default si falla
        'carbohidratos': goals_data.get('daily_carbs', 220)  # 220g default si falla
    }
