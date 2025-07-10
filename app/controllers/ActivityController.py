# app/controllers/ActivityController.py

from flask import render_template, request, redirect, url_for, flash 
from flask_login import login_required, current_user 
from app import app
from app.models.ActivityModel import save_daily_activity 


@app.route('/activity')
@login_required # Es buena práctica proteger también la vista de la página
def activity():
    # Puedes añadir lógica aquí para mostrar actividades previas si quieres
    return render_template('Activity/Activity.html')



@app.route('/register_activity', methods=['POST'])
@login_required
def register_activity():
    # Captura los datos enviados desde el formulario/JavaScript
    activity_name = request.form.get('activity_name')
    duration_minutes = request.form.get('duration_minutes', type=int)
    calories_burned = request.form.get('calories_burned', type=float)

    # Validación básica de los datos
    if not all([activity_name, duration_minutes is not None, calories_burned is not None]):
        flash("Datos de actividad incompletos. Por favor, asegúrate de seleccionar una actividad y la duración.", "warning")
        return redirect(url_for('activity')) # Redirige a la página de actividad

    # Usa current_user.id para obtener el ID del usuario logueado
    user_id = current_user.id

    # Llama a la función del modelo para guardar la actividad
    if save_daily_activity(user_id, activity_name, duration_minutes, calories_burned):
        flash(f"Actividad '{activity_name}' ({duration_minutes} min) registrada exitosamente!", "success")
    else:
        flash("Hubo un error al registrar la actividad. Inténtalo de nuevo.", "danger")
        
    # Redirige al usuario a otra página después de guardar (ej. el dashboard o la misma página de actividad)
    # Considera redirigir a 'activity' para que el usuario pueda ver las actividades recién añadidas
    return redirect(url_for('activity'))