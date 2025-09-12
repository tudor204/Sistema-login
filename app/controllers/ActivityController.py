from flask import render_template, request, jsonify
from flask_login import login_required, current_user
from app import app
from app.models.ActivityModel import (
    save_daily_activity,
    get_daily_activities_for_user,
    get_total_activity_minutes_today,
    update_activity,
    delete_activity
)
from datetime import datetime

# Función de ayuda para convertir objetos sqlite3.Row a diccionarios
def row_to_dict(row):
    if row is None:
        return None
    return dict(row)

@app.route('/activity')
@login_required
def activity():
    user_id = current_user.id
    today_date = datetime.now().strftime('%Y-%m-%d')
    activities_row_objects = get_daily_activities_for_user(user_id, date=today_date)
    activities_for_template = [row_to_dict(activity) for activity in activities_row_objects]
    total_minutes_today = get_total_activity_minutes_today(user_id, date=today_date)
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
        updated_activities_row_objects = get_daily_activities_for_user(user_id, date=today_date)
        formatted_activities = []
        for activity in updated_activities_row_objects:
            timestamp_str = activity['timestamp'] if isinstance(activity['timestamp'], str) else str(activity['timestamp'])
            formatted_activities.append({
                'id': activity['id'],
                'activity_name': activity['activity_name'],
                'duration_minutes': activity['duration_minutes'],
                'calories_burned': round(activity['calories_burned'], 2),
                'date_recorded': activity['date_recorded'],
                'timestamp': timestamp_str
            })
        total_minutes_today = get_total_activity_minutes_today(user_id, date=today_date)
        return jsonify({
            "success": True,
            "message": f"Actividad '{activity_name}' ({duration_minutes} min) registrada exitosamente!",
            "activities": formatted_activities,
            "total_minutes_today": total_minutes_today
        })
    else:
        return jsonify({"success": False, "message": "Hubo un error al registrar la actividad. Inténtalo de nuevo."}), 500

# 📌 Editar actividad
@app.route('/activity/edit/<int:activity_id>', methods=['POST'])
@login_required
def edit_activity(activity_id):
    activity_name = request.form.get('activity_name')
    duration_minutes = request.form.get('duration_minutes', type=int)
    calories_burned = request.form.get('calories_burned', type=float)
    user_id = current_user.id

    if update_activity(activity_id, user_id, activity_name, duration_minutes, calories_burned):
        # Obtener todas las actividades actualizadas
        today_date = datetime.now().strftime('%Y-%m-%d')
        activities_row_objects = get_daily_activities_for_user(user_id, date=today_date)
        formatted_activities = []
        for activity in activities_row_objects:
            timestamp_str = activity['timestamp'] if isinstance(activity['timestamp'], str) else str(activity['timestamp'])
            formatted_activities.append({
                'id': activity['id'],
                'activity_name': activity['activity_name'],
                'duration_minutes': activity['duration_minutes'],
                'calories_burned': round(activity['calories_burned'], 2),
                'date_recorded': activity['date_recorded'],
                'timestamp': timestamp_str
            })
        total_minutes_today = get_total_activity_minutes_today(user_id, date=today_date)
        return jsonify({"success": True, "message": "Actividad actualizada correctamente.", "activities": formatted_activities, "total_minutes_today": total_minutes_today})
    else:
        return jsonify({"success": False, "message": "Error al actualizar la actividad."}), 400

# 📌 Eliminar actividad
@app.route('/activity/delete/<int:activity_id>', methods=['POST'])
@login_required
def delete_activity_route(activity_id):
    user_id = current_user.id

    if delete_activity(activity_id, user_id):
        # Obtener todas las actividades actualizadas
        today_date = datetime.now().strftime('%Y-%m-%d')
        activities_row_objects = get_daily_activities_for_user(user_id, date=today_date)
        formatted_activities = []
        for activity in activities_row_objects:
            timestamp_str = activity['timestamp'] if isinstance(activity['timestamp'], str) else str(activity['timestamp'])
            formatted_activities.append({
                'id': activity['id'],
                'activity_name': activity['activity_name'],
                'duration_minutes': activity['duration_minutes'],
                'calories_burned': round(activity['calories_burned'], 2),
                'date_recorded': activity['date_recorded'],
                'timestamp': timestamp_str
            })
        total_minutes_today = get_total_activity_minutes_today(user_id, date=today_date)
        return jsonify({"success": True, "message": "Actividad eliminada correctamente.", "activities": formatted_activities, "total_minutes_today": total_minutes_today})
    else:
        return jsonify({"success": False, "message": "Error al eliminar la actividad."}), 400
