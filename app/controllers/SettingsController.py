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
    # Obtener las metas del usuario para mostrarlas en el formulario
    goals = get_user_goals(current_user.id)

    if request.method == 'POST':
        # 1. Recuperar todos los datos del formulario como texto sin procesar
        weight_str = request.form.get('weight')
        height_str = request.form.get('height')
        age_str = request.form.get('age')
        gender = request.form.get('gender')
        activity_level_from_form = request.form.get('activity_level')
        goal = request.form.get('goal')

        # 2. VALIDACIÓN: Asegurarse de que ningún campo esté vacío
        # La función all() devuelve True solo si todos los elementos de la lista son "verdaderos" (no vacíos o None)
        if not all([weight_str, height_str, age_str, gender, activity_level_from_form, goal]):
            flash('Por favor, rellena todos los campos para poder guardar.', 'danger')
            # Si algo falla, redirigimos de vuelta al formulario para que el usuario corrija
            return redirect(url_for('settings'))

        try:
            # 3. INTENTO DE CONVERSIÓN: Ahora que sabemos que no están vacíos, intentamos convertirlos
            weight = float(weight_str)
            height = int(height_str)
            age = int(age_str)

            # 4. VALIDACIÓN LÓGICA: Comprobar que los números tengan sentido
            if weight <= 0 or height <= 0 or age <= 0:
                flash('El peso, la altura y la edad deben ser números positivos.', 'danger')
                return redirect(url_for('settings'))
            
            # (La validación de género se puede hacer aquí también, pero como es un select, es menos probable que falle)
            if gender not in ['male', 'female']:
                 flash('Por favor, selecciona un género válido.', 'danger')
                 return redirect(url_for('settings'))

            # 5. PROCESAMIENTO: Si todas las validaciones pasan, continuamos con la lógica
            activity_level_mapped = {
                'sedentary': 'low',
                'light': 'low',
                'moderate': 'moderate',
                'active': 'high',
                'very_active': 'high'
            }.get(activity_level_from_form, 'low') # 'low' es un valor por defecto seguro

            # Guardar los datos en la base de datos
            save_user_initial_settings(current_user.id, weight, height, age, gender, activity_level_mapped, goal)
            flash('¡Configuración guardada correctamente! Ya puedes empezar.', 'success')
            return redirect(url_for('dashboard'))

        except ValueError:
            # Si la conversión de float() o int() falla (ej: el usuario escribe "abc")
            flash('Por favor, introduce valores numéricos válidos para peso, altura y edad.', 'danger')
            return redirect(url_for('settings'))
        
        except Exception as e:
            # Captura cualquier otro error que pueda ocurrir, por ejemplo, en la base de datos
            flash(f'Ocurrió un error inesperado al guardar los datos: {str(e)}', 'danger')
            return redirect(url_for('settings'))

    # Si la petición es GET, simplemente mostramos el formulario
    return render_template('Dashboard/settings_first_time.html', goals=goals)