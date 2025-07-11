from flask import render_template, request, flash, redirect, url_for 
from flask_login import login_required, current_user
from app import app
from app.conexion import get_db_cursor
import datetime
from app.models.ActivityModel import get_total_activity_minutes_today,get_total_calories_burned_today

@app.route('/dashboard')
@login_required
def dashboard():
    with get_db_cursor() as cur:
        # Obtener metas del usuario
        cur.execute("SELECT * FROM user_goals WHERE user_id = ?", (current_user.id,))
        goals = cur.fetchone() or {
            'daily_calories': 2000, 
            'daily_proteins': 50, 
            'daily_water': 2,
            'daily_fats': 60,
            'daily_carbs': 250,
            'daily_activity': 30,
            'water_consumed': 0 
        }
        if not isinstance(goals, dict):
            goals = dict(goals)

        # Estadísticas de hoy (calorías, proteínas, grasas, carbohidratos)
        cur.execute("""
            SELECT SUM(calories) as calories, 
                   SUM(proteins) as proteins,
                   SUM(fats) as fats,
                   SUM(carbs) as carbs
            FROM food_entries
            WHERE user_id = ? AND date(date) = date('now')
        """, (current_user.id,))
        today_stats = cur.fetchone() or {'calories': 0, 'proteins': 0, 'fats': 0, 'carbs': 0}
        if not isinstance(today_stats, dict):
            today_stats = dict(today_stats)
        
        today_calories = today_stats.get('calories') or 0
        # Obtener calorías quemadas por actividad hoy
        burned_calories = get_total_calories_burned_today(current_user.id)

        # Calorías netas = calorías ingeridas - calorías gastadas
        net_calories = today_calories - burned_calories

        today_proteins = today_stats.get('proteins') or 0
        today_fats = today_stats.get('fats') or 0
        today_carbs = today_stats.get('carbs') or 0

        # Alimentos recientes
        cur.execute("""
            SELECT food_name, calories, proteins, fats, carbs, date
            FROM food_entries
            WHERE user_id = ?
            ORDER BY date DESC, created_at DESC 
            LIMIT 5
        """, (current_user.id,))
        recent_foods = cur.fetchall()

    # Obtener minutos totales de actividad hoy
    activity_minutes = get_total_activity_minutes_today(current_user.id)
    today_stats['activity'] = activity_minutes
    daily_activity = goals.get('daily_activity', 30) or 30
    activity_percentage = min(100, (activity_minutes / daily_activity) * 100) if daily_activity > 0 else 0

    # Calcular porcentajes para todos los macros
    daily_calories = goals.get('daily_calories', 2000) or 2000
    daily_proteins = goals.get('daily_proteins', 50) or 50
    daily_fats = goals.get('daily_fats', 60) or 60
    daily_carbs = goals.get('daily_carbs', 250) or 250
    daily_water_ml = (goals.get('daily_water', 2) or 2) * 1000 # Convertir litros a ml para el cálculo
    water_consumed_ml = goals.get('water_consumed', 0) or 0 # Obtener el agua consumida
    

    calories_percentage = min(100, (today_calories / daily_calories) * 100)
    proteins_percentage = min(100, (today_proteins / daily_proteins) * 100)
    fats_percentage = min(100, (today_fats / daily_fats) * 100)
    carbs_percentage = min(100, (today_carbs / daily_carbs) * 100)
    
    # Calcular porcentaje de agua
    water_percentage = min(100, (water_consumed_ml / daily_water_ml) * 100) if daily_water_ml > 0 else 0


    return render_template('Dashboard/dashboard.html',
        goals=goals,
        today_stats=today_stats,
        recent_foods=recent_foods,
        calories_percentage=round(calories_percentage, 1),
        proteins_percentage=round(proteins_percentage, 1),
        fats_percentage=round(fats_percentage, 1),
        carbs_percentage=round(carbs_percentage, 1),
        water_percentage=round(water_percentage, 1),
        water_consumed_ml=water_consumed_ml,
        activity_minutes=activity_minutes,
        activity_percentage=round(activity_percentage, 1),
        net_calories=net_calories,
        burned_calories=burned_calories,
        calories_in=today_calories

    )

@app.route('/add_water_intake', methods=['POST'])
@login_required
def add_water_intake():
    water_quantity_ml = request.form.get('water-quantity', type=float)

    if water_quantity_ml is None or water_quantity_ml <= 0:
        flash('Cantidad de agua inválida.', 'danger')
        return redirect(url_for('dashboard'))

    try:
        with get_db_cursor() as cur:
            # Actualizar la columna water_consumed para el usuario actual
            cur.execute("""
                UPDATE user_goals 
                SET water_consumed = IFNULL(water_consumed, 0) + ?,
                    updated_at = ?
                WHERE user_id = ?
            """, (water_quantity_ml, datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), current_user.id))
            
            flash(f'{water_quantity_ml} ml de agua registrados.', 'success')
    except Exception as e:
        flash(f'Error al registrar el agua: {str(e)}', 'danger')
        print(f"Error al registrar el agua: {e}") # Para depuración en la consola

    return redirect(url_for('dashboard'))
