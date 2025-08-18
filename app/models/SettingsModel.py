# models/settings_model.py
from app.conexion import get_db_cursor
import datetime

def save_user_goals(user_id, daily_calories, daily_proteins, daily_water, daily_fats, daily_carbs, daily_activity):
    with get_db_cursor() as cur:
        cur.execute("""
            INSERT OR REPLACE INTO user_goals 
            (user_id, daily_calories, daily_proteins, daily_water, daily_fats, daily_carbs, daily_activity, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            user_id,
            daily_calories,
            daily_proteins,
            daily_water,
            daily_fats,
            daily_carbs,
            daily_activity,
            datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        ))

def get_user_goals(user_id):
    with get_db_cursor() as cur:
        cur.execute("SELECT * FROM user_goals WHERE user_id = ?", (user_id,))
        goals = cur.fetchone() or {
            'daily_calories': 2500,
            'daily_proteins': 100,
            'daily_water': 2.5,
            'daily_fats': 90,
            'daily_carbs': 300,
            'daily_activity': 60,
            'water_consumed': 0
        }
        if not isinstance(goals, dict):
            goals = dict(goals)
        return goals



def calculate_macros(weight, height, age, gender, activity_level, goal):
    # Calcular BMR con Mifflin-St Jeor
    if gender == 'male':
        bmr = 10 * weight + 6.25 * height - 5 * age + 5
    else:
        bmr = 10 * weight + 6.25 * height - 5 * age - 161

    # Multiplicador según nivel de actividad
    activity_multipliers = {
        'low': 1.2,
        'moderate': 1.55,
        'high': 1.9
    }
    tdee = bmr * activity_multipliers.get(activity_level, 1.2)

    # Ajuste según objetivo
    if goal == 'gain':
        tdee += 300
    elif goal == 'lose':
        tdee -= 300

    # Macronutrientes (aprox)
    proteins = weight * 2.2  # 2.2 g/kg de peso
    fats = weight * 1        # 1 g/kg de peso
    calories_from_protein = proteins * 4
    calories_from_fat = fats * 9
    remaining_calories = tdee - (calories_from_protein + calories_from_fat)
    carbs = remaining_calories / 4

    return round(tdee), round(proteins), round(fats), round(carbs)

def calculate_daily_activity_minutes(activity_level: str, goal: str, age: int = None) -> int:
    """
    Devuelve minutos/día recomendados según objetivo y nivel de actividad.
    Reglas simples y claras (puedes ajustarlas si lo deseas):
      - Objetivo:
          - 'lose' (pérdida de peso): base 50 min/día
          - 'maintain' (mantenimiento): base 35 min/día
          - 'gain' (hipertrofia): base 30 min/día (más foco en fuerza que en cardio)
      - Nivel de actividad:
          - 'low':     +10 min
          - 'moderate': +0 min
          - 'high':    -5 min
      - Ajuste por edad (opcional, suave):
          - si age y age >= 55: -5 min
    Se redondea a múltiplos de 5 y se acota entre 20 y 90.
    """
    goal_map = {
        'lose': 85,
        'maintain': 60,
        'gain': 50
    }
    base = goal_map.get(goal, 35)

    level_adj = {
        'low': 10,
        'moderate': 0,
        'high': -5
    }.get(activity_level, 0)

    age_adj = -5 if (age is not None and age >= 55) else 0

    minutes = base + level_adj + age_adj
    minutes = max(20, min(90, minutes))  # clamp
    # Redondeo a 5
    minutes = int(round(minutes / 5.0) * 5)
    return minutes


def save_user_initial_settings(user_id, weight, height, age, gender, activity_level, goal):
    calories, proteins, fats, carbs = calculate_macros(weight, height, age, gender, activity_level, goal)
    with get_db_cursor() as cur:
            daily_activity = calculate_daily_activity_minutes(activity_level, goal, age)

    with get_db_cursor() as cur:
        cur.execute("""
            INSERT OR REPLACE INTO user_goals 
            (user_id, weight, height, age, gender, goal, daily_calories, daily_proteins, daily_fats, daily_carbs, daily_water, daily_activity, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            user_id, weight, height, age, gender, goal,
            calories, proteins, fats, carbs,
            2.5, daily_activity, datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        ))

        
