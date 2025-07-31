from flask import render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from app import app
from app.conexion import get_db_cursor
import datetime
from app.models.ActivityModel import get_total_activity_minutes_today, get_total_calories_burned_today
from app.models.UsersModel import get_user_preferences
import random
import os
import sys
import logging # Importa el módulo logging

# Configura el logging al inicio del archivo o en tu archivo principal de la aplicación (app.py)
# Asegúrate de que el nivel sea DEBUG para ver todos los mensajes.
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

tips_path = os.path.join(os.path.dirname(__file__), '..', 'static', 'utils')
sys.path.append(tips_path)
from app.utils.tips import nutritional_tips

@app.route('/dashboard')
@login_required
def dashboard():
    logging.debug(f"Accediendo a la ruta /dashboard para el usuario: {current_user.id}")

    with get_db_cursor() as cur:
        # Obtener metas del usuario de la base de datos
        cur.execute("SELECT * FROM user_goals WHERE user_id = ?", (current_user.id,))
        goals_raw = cur.fetchone() # Esto devuelve un objeto Row o None

        logging.debug(f"Datos de 'user_goals' recuperados de la DB (raw): {goals_raw}")

        # Si no hay ninguna fila para el usuario, significa que no ha completado la configuración inicial
        if not goals_raw:
            flash('Por favor, completa tu configuración inicial para empezar.', 'warning')
            # Redirige a la ruta 'settings' que maneja si es la primera vez o no
            return redirect(url_for('settings'))

        # Convierte el objeto Row de la base de datos a un diccionario para un acceso más fácil
        goals = dict(goals_raw)
        logging.debug(f"Datos de 'user_goals' después de la conversión a dict: {goals}")

        # --- VALIDACIÓN CRÍTICA ---
        # Validar si faltan campos esenciales de la configuración inicial O las macros calculadas.
        # Es crucial que estos campos existan y tengan valores válidos (no None o 0) después de la configuración inicial.
        required_fields_for_dashboard = [
            'weight', 'height', 'age', 'gender', 'goal',
            'daily_calories', 'daily_proteins', 'daily_fats', 'daily_carbs',
            'daily_water', 'daily_activity'
        ]

        # Comprueba si alguno de los campos requeridos está ausente o tiene un valor "falso" (None, 0, cadena vacía)
        # Nota: 'water_consumed' puede ser 0 inicialmente, por eso no está en esta lista de validación estricta.
        if not all(goals.get(k) is not None and goals.get(k) != 0 for k in required_fields_for_dashboard):
            missing_or_zero_fields = [k for k in required_fields_for_dashboard if goals.get(k) is None or goals.get(k) == 0]
            logging.warning(f"Faltan campos de configuración inicial o macros calculadas para el usuario {current_user.id}. "
                            f"Campos faltantes/cero: {missing_or_zero_fields}. Redirigiendo a settings.")
            flash('Parece que tu configuración inicial o tus metas no están completas. Por favor, revísalas.', 'warning')
            # Redirige a la ruta 'settings' para que el usuario pueda completar o corregir su perfil
            return redirect(url_for('settings'))

        # Obtener estadísticas de alimentos de hoy
        cur.execute("""
            SELECT SUM(calories) as calories,
                   SUM(proteins) as proteins,
                   SUM(fats) as fats,
                   SUM(carbs) as carbs
            FROM food_entries
            WHERE user_id = ? AND date(date) = date('now')
        """, (current_user.id,))
        today_stats = dict(cur.fetchone() or {'calories': 0, 'proteins': 0, 'fats': 0, 'carbs': 0})
        logging.debug(f"Estadísticas de alimentos de hoy: {today_stats}")

        today_calories = today_stats.get('calories') or 0
        today_proteins = today_stats.get('proteins') or 0
        today_fats = today_stats.get('fats') or 0
        today_carbs = today_stats.get('carbs') or 0

        # Calorías quemadas y netas
        burned_calories = get_total_calories_burned_today(current_user.id)
        net_calories = today_calories - burned_calories
        logging.debug(f"Calorías netas: {net_calories}, Quemadas: {burned_calories}, Consumidas: {today_calories}")

        # Alimentos recientes
        cur.execute("""
            SELECT food_name, calories, proteins, fats, carbs, date
            FROM food_entries
            WHERE user_id = ?
            ORDER BY date DESC, created_at DESC
            LIMIT 5
        """, (current_user.id,))
        recent_foods = cur.fetchall()
        logging.debug(f"Alimentos recientes: {recent_foods}")

    # Actividad física
    activity_minutes = get_total_activity_minutes_today(current_user.id)
    today_stats['activity'] = activity_minutes # Añadir al diccionario today_stats
    # Asegúrate de que daily_activity se obtiene de goals, con un valor por defecto si no existe
    daily_activity = goals.get('daily_activity') or 60 # Default a 60 minutos si no está en goals
    activity_percentage = min(100, (activity_minutes / daily_activity) * 100) if daily_activity > 0 else 0
    logging.debug(f"Actividad: {activity_minutes} min, Meta: {daily_activity} min, Porcentaje: {activity_percentage}%")

    # Metas nutricionales (estos valores deberían venir de la configuración inicial guardada)
    daily_calories = goals.get('daily_calories') or 2000
    daily_proteins = goals.get('daily_proteins') or 50
    daily_fats = goals.get('daily_fats') or 60
    daily_carbs = goals.get('daily_carbs') or 250
    daily_water_ml = (goals.get('daily_water') or 2) * 1000 # Convertir litros a ml
    water_consumed_ml = goals.get('water_consumed') or 0
    logging.debug(f"Metas diarias: Calorías={daily_calories}, Proteínas={daily_proteins}, Grasas={daily_fats}, Carbs={daily_carbs}, Agua={daily_water_ml}ml")
    logging.debug(f"Agua consumida: {water_consumed_ml}ml")

    # Porcentajes (añadir comprobación de división por cero para evitar errores)
    calories_percentage = min(100, (today_calories / daily_calories) * 100) if daily_calories > 0 else 0
    proteins_percentage = min(100, (today_proteins / daily_proteins) * 100) if daily_proteins > 0 else 0
    fats_percentage = min(100, (today_fats / daily_fats) * 100) if daily_fats > 0 else 0
    carbs_percentage = min(100, (today_carbs / daily_carbs) * 100) if daily_carbs > 0 else 0
    water_percentage = min(100, (water_consumed_ml / daily_water_ml) * 100) if daily_water_ml > 0 else 0
    logging.debug(f"Porcentajes: Calorías={calories_percentage}%, Proteínas={proteins_percentage}%, Grasas={fats_percentage}%, Carbs={carbs_percentage}%, Agua={water_percentage}%")

    # Tips y preferencias
    prefs = get_user_preferences(current_user.id)
    # Asegúrate de que prefs no sea None antes de intentar .get()
    tips_to_show = random.sample(nutritional_tips, k=min(2, len(nutritional_tips))) if prefs and prefs.get("auto_suggestions") else []
    logging.debug(f"Tips a mostrar: {tips_to_show}")

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
        calories_in=today_calories,
        tips=tips_to_show
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
        logging.error(f"Error al registrar el agua: {e}") # Usar logging.error para errores

    return redirect(url_for('dashboard'))
