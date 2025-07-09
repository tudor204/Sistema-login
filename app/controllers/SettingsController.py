from flask import render_template, request, flash, redirect, url_for # Asegúrate de importar redirect y url_for
from flask_login import login_required, current_user
from app import app
from app.conexion import get_db_cursor
import datetime

@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    if request.method == 'POST':
        daily_calories = request.form.get('daily_calories', type=int) or 0
        daily_proteins = request.form.get('daily_proteins', type=int) or 0
        daily_water = request.form.get('daily_water', type=int) or 0
        daily_fats = request.form.get('daily_fats', type=int) or 0
        daily_carbs = request.form.get('daily_carbs', type=int) or 0
        daily_activity = request.form.get('daily_activity', type=int) or 0

        if not all([
            1000 <= daily_calories <= 5000, 
            daily_proteins > 0, 
            daily_water > 0,
            daily_fats > 0,
            daily_carbs > 0,
            daily_activity >= 0
        ]):
            flash('Valores inválidos para los objetivos diarios.', 'danger')
            # Si los valores son inválidos, se queda en la página de settings
            # y muestra el mensaje flash.
            # No se necesita un 'return redirect' aquí si quieres que el formulario
            # se mantenga con los datos para que el usuario los corrija.
        else:
            try: # Añadir un bloque try-except para la operación de base de datos
                with get_db_cursor() as cur:
                    cur.execute("""
                        INSERT OR REPLACE INTO user_goals 
                        (user_id, daily_calories, daily_proteins, daily_water, daily_fats, daily_carbs, daily_activity, updated_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (current_user.id, daily_calories, daily_proteins, daily_water, daily_fats, daily_carbs, daily_activity, datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
                    flash('Configuración guardada', 'success')
                    # ¡AQUÍ ESTÁ EL CAMBIO! Redirigir al dashboard
                    return redirect(url_for('dashboard'))
            except Exception as e:
                flash(f'Error al guardar la configuración: {str(e)}', 'danger')
                print(f"Error al guardar configuración: {e}") # Para depuración
    
    # Este bloque se ejecuta si el método es GET, o si el POST falló la validación
    # o hubo un error en la BD y no se redirigió.
    with get_db_cursor() as cur:
        cur.execute("SELECT * FROM user_goals WHERE user_id = ?", (current_user.id,))
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

    return render_template('Dashboard/settings.html', goals=goals)

