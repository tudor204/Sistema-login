from flask import render_template, redirect, url_for, flash, request, current_app, session
from flask_login import logout_user, login_required, current_user
from app import app
from werkzeug.utils import secure_filename
import os


from app.models.UsersModel import (
    allowed_file,
    get_user_profile,
    update_user_profile,
    update_user_preferences,
    get_user_preferences,
    check_user_password,
    update_user_password,
    check_email_exists,
    update_user_email,
    delete_user_account
)

@app.context_processor
def inject_prefs():
    if current_user.is_authenticated:
        prefs = get_user_preferences(current_user.id)  # función que recupera las prefs
        return dict(prefs=prefs)
    return dict(prefs=None)


@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        birth_date = request.form.get('birth_date', '').strip()
        prefs = get_user_preferences(current_user.id)

        try:
            height = float(request.form.get('height_cm', ''))
        except (TypeError, ValueError):
            height = None

        try:
            weight = float(request.form.get('weight_kg', ''))
        except (TypeError, ValueError):
            weight = None

        # Convertir de vuelta a kg/cm si el usuario envía lb/in
        if prefs.get('units') == 'lb/in':
            if weight:
                weight = round(weight / 2.20462, 1)
            if height:
                height = round(height / 0.393701, 1)

        height_cm = int(height) if height else None
        weight_kg = int(weight) if weight else None


        gender = request.form.get('gender', '').strip()
        activity_level = request.form.get('activity_level', '').strip()
        goal = request.form.get('goal', '').strip()

        photo = request.files.get('profile_photo')
        filename = None
        if photo and allowed_file(photo.filename):
            filename = secure_filename(photo.filename)
            upload_folder = os.path.join(current_app.root_path, 'static', 'images', 'profile_photo')
            os.makedirs(upload_folder, exist_ok=True)
            photo.save(os.path.join(upload_folder, filename))

        if not full_name:
            flash("El nombre completo no puede estar vacío.", "warning")
        else:
            update_user_profile(current_user.id, full_name, birth_date, height_cm, weight_kg, gender, activity_level, goal, filename)
            flash("Perfil actualizado correctamente", "success")
            return redirect(url_for('profile'))

    user_data = get_user_profile(current_user.id)
    prefs = get_user_preferences(current_user.id) 
    # Si el usuario prefiere lb/in, convertimos los valores para mostrarlos
    if prefs.get('units') == 'lb/in':
        if user_data['weight_kg']:
            user_data['weight_kg'] = round(user_data['weight_kg'] * 2.20462, 1)
        if user_data['height_cm']:
            user_data['height_cm'] = round(user_data['height_cm'] * 0.393701, 1)

    return render_template('Users/profile.html', user=user_data)


@app.route('/configuracion', methods=['GET', 'POST'])
@login_required
def configuracion():
    if request.method == 'POST':
        preferencias = {
            "dark_mode": request.form.get("dark_mode") == "on",
            "units": request.form.get("units", "kg/cm"),
            "auto_suggestions": request.form.get("auto_suggestions") == "on",
            "language": request.form.get("language", "es")
        }
        update_user_preferences(current_user.id, preferencias)

        # Aquí actualizas la sesión para que Flask-Babel detecte el idioma
        session['user_lang'] = preferencias['language']

        flash("Preferencias actualizadas correctamente", "success")
        return redirect(url_for('configuracion'))

    prefs = get_user_preferences(current_user.id)
    return render_template('Users/configuracion.html', prefs=prefs)


@app.route('/cambiar-password', methods=['GET', 'POST'])
@login_required
def cambiar_password():
    if request.method == 'POST':
        current_password = request.form.get('current_password', '')
        new_password = request.form.get('new_password', '')
        confirm_password = request.form.get('confirm_password', '')

        if not current_password or not new_password or not confirm_password:
            flash("Por favor completa todos los campos.", "warning")
        elif new_password != confirm_password:
            flash("Las nuevas contraseñas no coinciden.", "danger")
        elif not check_user_password(current_user.id, current_password):
            flash("La contraseña actual es incorrecta.", "danger")
        else:
            update_user_password(current_user.id, new_password)
            flash("Contraseña actualizada correctamente.", "success")
            return redirect(url_for('configuracion'))

    return render_template("Users/cambiar_password.html")


@app.route('/cambiar-email', methods=['GET', 'POST'])
@login_required
def cambiar_email():
    if request.method == 'POST':
        nuevo_email = request.form.get('nuevo_email', '').strip()

        if not nuevo_email:
            flash("Por favor, ingresa un nuevo correo electrónico.", "warning")
        elif check_email_exists(nuevo_email, current_user.id):
            flash("Ese correo electrónico ya está en uso.", "danger")
        else:
            update_user_email(current_user.id, nuevo_email)
            flash("Correo electrónico actualizado correctamente.", "success")
            return redirect(url_for('configuracion'))

    return render_template("Users/cambiar_email.html")


@app.route('/eliminar-cuenta', methods=['GET', 'POST'])
@login_required
def eliminar_cuenta():
    if request.method == 'POST':
        password = request.form.get('password', '')

        if not password:
            flash("Debes ingresar tu contraseña para confirmar.", "warning")
        elif not check_user_password(current_user.id, password):
            flash("Contraseña incorrecta. La cuenta no ha sido eliminada.", "danger")
        else:
            delete_user_account(current_user.id)
            logout_user()
            flash("Tu cuenta ha sido eliminada correctamente.", "success")
            return redirect(url_for('index'))

    flash("¿Estás seguro de que quieres eliminar tu cuenta? Esta acción no se puede deshacer.", "danger")
    return render_template("Users/eliminar_cuenta.html")


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Sesión cerrada', 'info')
    return redirect(url_for('index'))