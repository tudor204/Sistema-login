from flask import render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from app import app
from app.models.SettingsModel import (
    get_user_goals,
    save_user_initial_settings,
    # save_user_goals # No se usa directamente en esta ruta, pero es parte del modelo
)

@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    # Obtener las metas del usuario al inicio, para determinar qué plantilla renderizar
    goals = get_user_goals(current_user.id)

    if request.method == 'POST':
        # Recuperar datos del formulario
        weight = float(request.form.get('weight', 0))
        height = int(request.form.get('height', 0))
        age = int(request.form.get('age', 0))
        gender = request.form.get('gender')
        
        # *** CAMBIO CLAVE AQUÍ ***
        # El nombre del campo en el HTML es 'activity_level', no 'activity'
        activity_level_from_form = request.form.get('activity_level')
        goal = request.form.get('goal')

        # Mapear los niveles de actividad de la vista a los que el modelo 'calculate_macros' espera
        # Esto asegura que la lógica del modelo reciba un valor reconocido
        activity_level_mapped = {
            'sedentary': 'low',
            'light': 'low',
            'moderate': 'moderate',
            'active': 'high',
            'very_active': 'high'
        }.get(activity_level_from_form, 'low') # Por defecto a 'low' si no se encuentra el mapeo

        # Validaciones básicas
        if weight <= 0 or height <= 0 or age <= 0 or gender not in ['male', 'female']:
            flash('Todos los datos deben ser válidos (peso, altura, edad deben ser mayores a 0, y el sexo debe ser hombre o mujer).', 'danger')
        else:
            try:
                # Pasar el nivel de actividad mapeado a la función del modelo
                save_user_initial_settings(current_user.id, weight, height, age, gender, activity_level_mapped, goal)
                flash('Configuración guardada correctamente', 'success')
                return redirect(url_for('dashboard'))
            except Exception as e:
                # Manejo de errores en caso de problemas al guardar en la base de datos
                flash(f'Error al guardar los datos: {str(e)}', 'danger')
    
    # Si el usuario ya tiene peso y altura registrados (indicando que ya hizo la configuración inicial),
    # se le redirige a la plantilla de configuración general.
    # De lo contrario, se le muestra la plantilla de primera vez.
    if goals.get('weight') and goals.get('height'):
        # Asumiendo que 'settings.html' es para editar la configuración existente
        return render_template('Dashboard/settings.html', goals=goals)
    
    # 'settings_first_time.html' es para la configuración inicial
    return render_template('Dashboard/settings_first_time.html', goals=goals)
