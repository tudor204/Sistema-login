from flask import render_template, redirect, url_for, flash, request
from flask_login import logout_user, login_required, current_user
from app.conexion import get_db_cursor
from app.models.UsersModel import allowed_file
from app import app
import json
import os
from werkzeug.utils import secure_filename
from flask import current_app
from werkzeug.security import check_password_hash, generate_password_hash


@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        birth_date = request.form.get('birth_date', '').strip()
        
        try:
            height_cm = int(request.form.get('height_cm', ''))
        except (TypeError, ValueError):
            height_cm = None
        try:
            weight_kg = int(request.form.get('weight_kg', ''))
        except (TypeError, ValueError):
            weight_kg = None

        gender = request.form.get('gender', '').strip()
        activity_level = request.form.get('activity_level', '').strip()
        goal = request.form.get('goal', '').strip()

        # --- Manejo de foto ---
        photo = request.files.get('profile_photo')
        filename = None
        if photo and allowed_file(photo.filename):
            filename = secure_filename(photo.filename)
            upload_folder = os.path.join(current_app.root_path, 'static', 'images', 'profile_photo')
            os.makedirs(upload_folder, exist_ok=True)
            photo.save(os.path.join(upload_folder, filename))
        # ----------------------

        if not full_name:
            flash("El nombre completo no puede estar vacío.", "warning")
        else:
            try:
                with get_db_cursor() as cursor:
                    if filename:
                        cursor.execute("""
                            UPDATE loggin 
                            SET full_name = ?, birth_date = ?, height_cm = ?, weight_kg = ?, gender = ?, activity_level = ?, goal = ?, profile_photo = ?
                            WHERE id = ?
                        """, (full_name, birth_date, height_cm, weight_kg, gender, activity_level, goal, filename, current_user.id))
                    else:
                        cursor.execute("""
                            UPDATE loggin 
                            SET full_name = ?, birth_date = ?, height_cm = ?, weight_kg = ?, gender = ?, activity_level = ?, goal = ?
                            WHERE id = ?
                        """, (full_name, birth_date, height_cm, weight_kg, gender, activity_level, goal, current_user.id))
                    flash("Perfil actualizado correctamente", "success")
                    return redirect(url_for('profile'))
            except Exception as e:
                flash(f"Error al actualizar el perfil: {e}", "danger")
                print(f"Error al actualizar perfil: {e}")

    with get_db_cursor() as cursor:
        cursor.execute("""
            SELECT username, email, full_name, birth_date, height_cm, weight_kg, gender, activity_level, goal, profile_photo
            FROM loggin 
            WHERE id = ?
        """, (current_user.id,))
        user_data = cursor.fetchone()
        if not isinstance(user_data, dict):
            user_data = dict(user_data)

    return render_template('Users/profile.html', user=user_data)

@app.route('/configuracion', methods=['GET', 'POST'])
@login_required
def configuracion():
    if request.method == 'POST':
        # Recoger los datos del formulario
        preferencias = {
            "dark_mode": request.form.get("dark_mode") == "on",
            "units": request.form.get("units", "kg/cm"),
            "auto_suggestions": request.form.get("auto_suggestions") == "on"
        }

        try:
            with get_db_cursor() as cursor:
                cursor.execute("""
                    UPDATE loggin SET preferences = ?
                    WHERE id = ?
                """, (json.dumps(preferencias), current_user.id))
                flash("Preferencias actualizadas correctamente", "success")
                return redirect(url_for('configuracion'))
        except Exception as e:
            flash(f"Error al guardar preferencias: {e}", "danger")

    # Cargar preferencias actuales
    with get_db_cursor() as cursor:
        cursor.execute("SELECT preferences FROM loggin WHERE id = ?", (current_user.id,))
        row = cursor.fetchone()
        prefs = {}
        if row and row["preferences"]:
            try:
                prefs = json.loads(row["preferences"])
            except Exception:
                prefs = {}

    return render_template('Users/configuracion.html', prefs=prefs)

@app.route('/cambiar-password', methods=['GET', 'POST'])
@login_required
def cambiar_password():
    if request.method == 'POST':
        current_password = request.form.get('current_password', '')
        new_password = request.form.get('new_password', '')
        confirm_password = request.form.get('confirm_password', '')

        # Verificar que no esté vacío
        if not current_password or not new_password or not confirm_password:
            flash("Por favor completa todos los campos.", "warning")
            return redirect(url_for('cambiar_password'))

        # Verificar que coincidan
        if new_password != confirm_password:
            flash("Las nuevas contraseñas no coinciden.", "danger")
            return redirect(url_for('cambiar_password'))

        # Verificar contraseña actual
        with get_db_cursor() as cursor:
            cursor.execute("SELECT password FROM loggin WHERE id = ?", (current_user.id,))
            row = cursor.fetchone()
            if row and not check_password_hash(row["password"], current_password):
                flash("La contraseña actual es incorrecta.", "danger")
                return redirect(url_for('cambiar_password'))

            # Actualizar nueva contraseña
            hashed_pw = generate_password_hash(new_password)
            cursor.execute("UPDATE loggin SET password = ? WHERE id = ?", (hashed_pw, current_user.id))
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
            return redirect(url_for('cambiar_email'))

        with get_db_cursor() as cursor:
            # Verificar si ya existe ese email en otro usuario
            cursor.execute("SELECT id FROM loggin WHERE email = ? AND id != ?", (nuevo_email, current_user.id))
            existing = cursor.fetchone()
            if existing:
                flash("Ese correo electrónico ya está en uso.", "danger")
                return redirect(url_for('cambiar_email'))

            # Actualizar correo electrónico
            cursor.execute("UPDATE loggin SET email = ? WHERE id = ?", (nuevo_email, current_user.id))
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
            return redirect(url_for('eliminar_cuenta'))

        with get_db_cursor() as cursor:
            cursor.execute("SELECT password FROM loggin WHERE id = ?", (current_user.id,))
            user = cursor.fetchone()

            if not user or not check_password_hash(user["password"], password):
                flash("Contraseña incorrecta. La cuenta no ha sido eliminada.", "danger")
                return redirect(url_for('eliminar_cuenta'))

            # Eliminar cuenta
            cursor.execute("DELETE FROM loggin WHERE id = ?", (current_user.id,))
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

