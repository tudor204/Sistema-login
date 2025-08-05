from flask import render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from app import app
from app.models.SettingsModel import (
    get_user_goals,
    save_user_initial_settings,
)

@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    # Obtener las metas del usuario
    goals = get_user_goals(current_user.id)

    if request.method == 'POST':
        # Recuperar datos del formulario
        weight = float(request.form.get('weight', 0))
        height = int(request.form.get('height', 0))
        age = int(request.form.get('age', 0))
        gender = request.form.get('gender')

        activity_level_from_form = request.form.get('activity_level')
        goal = request.form.get('goal')

        activity_level_mapped = {
            'sedentary': 'low',
            'light': 'low',
            'moderate': 'moderate',
            'active': 'high',
            'very_active': 'high'
        }.get(activity_level_from_form, 'low')

        if weight <= 0 or height <= 0 or age <= 0 or gender not in ['male', 'female']:
            flash('Todos los datos deben ser válidos (peso, altura, edad deben ser mayores a 0, y el sexo debe ser hombre o mujer).', 'danger')
        else:
            try:
                save_user_initial_settings(current_user.id, weight, height, age, gender, activity_level_mapped, goal)
                flash('Configuración guardada correctamente', 'success')
                return redirect(url_for('dashboard'))
            except Exception as e:
                flash(f'Error al guardar los datos: {str(e)}', 'danger')

    # Siempre renderiza la vista de configuración inicial
    return render_template('Dashboard/settings_first_time.html', goals=goals)
