from flask import render_template, request, jsonify
from flask_login import login_required, current_user
from app import app
from app.models.ActivityModel import (
    save_daily_activity,
    get_daily_activities_for_user,
    get_total_activity_minutes_today
)
from datetime import datetime

# Función de ayuda para convertir objetos sqlite3.Row a diccionarios
def row_to_dict(row):
    if row is None:
        return None
    # Convierte sqlite3.Row a un diccionario.
    # Esto asegura que el filtro tojson de Jinja y jsonify puedan manejarlo.
    return dict(row)

@app.route('/activity')
@login_required
def activity():
    user_id = current_user.id
    today_date = datetime.now().strftime('%Y-%m-%d')
    
    # Obtener actividades como objetos Row
    activities_row_objects = get_daily_activities_for_user(user_id, date=today_date)
    
    # Convertir cada objeto Row a un diccionario
    activities_for_template = [row_to_dict(activity) for activity in activities_row_objects]

    # Obtener total de minutos realizados hoy
    total_minutes_today = get_total_activity_minutes_today(user_id, date=today_date)

    # Pasar las actividades y el total de minutos a la plantilla
    return render_template('Activity/Activity.html', activities=activities_for_template, total_minutes_today=total_minutes_today)

@app.route('/register_activity', methods=['POST'])
@login_required
def register_activity():
    activity_name = request.form.get('activity_name')
    duration_minutes = request.form.get('duration_minutes', type=int)
    calories_burned = request.form.get('calories_burned', type=float)

    if not all([activity_name, duration_minutes is not None, calories_burned is not None]):
        return jsonify({"success": False, "message": "Datos de actividad incompletos. Asegúrate de seleccionar una actividad y duración."}), 400

    user_id = current_user.id

    if save_daily_activity(user_id, activity_name, duration_minutes, calories_burned):
        today_date = datetime.now().strftime('%Y-%m-%d')
        
        # Obtener actividades actualizadas como objetos Row
        updated_activities_row_objects = get_daily_activities_for_user(user_id, date=today_date)

        # Convertir cada objeto Row a un diccionario para la respuesta JSON
        formatted_activities = []
        for activity in updated_activities_row_objects:
            # Asegurarse de que el timestamp sea un string, si no lo es ya
            timestamp_str = activity['timestamp'] if isinstance(activity['timestamp'], str) else str(activity['timestamp'])
            formatted_activities.append({
                'activity_name': activity['activity_name'],
                'duration_minutes': activity['duration_minutes'],
                'calories_burned': round(activity['calories_burned'], 2),
                'date_recorded': activity['date_recorded'],
                'timestamp': timestamp_str
            })

        # Obtener minutos totales actualizados
        total_minutes_today = get_total_activity_minutes_today(user_id, date=today_date)

        return jsonify({
            "success": True,
            "message": f"Actividad '{activity_name}' ({duration_minutes} min) registrada exitosamente!",
            "activities": formatted_activities,
            "total_minutes_today": total_minutes_today
        })
    else:
        return jsonify({"success": False, "message": "Hubo un error al registrar la actividad. Inténtalo de nuevo."}), 500
