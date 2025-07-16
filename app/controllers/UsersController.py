from flask import render_template, redirect, url_for, flash, request
from flask_login import logout_user, login_required, current_user
from app.conexion import get_db_cursor
from app import app

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

        if not full_name:
            flash("El nombre completo no puede estar vacío.", "warning")
        else:
            try:
                with get_db_cursor() as cursor:
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
            SELECT username, email, full_name, birth_date, height_cm, weight_kg, gender, activity_level, goal
            FROM loggin 
            WHERE id = ?
        """, (current_user.id,))
        user_data = cursor.fetchone()
        if not isinstance(user_data, dict):
            user_data = dict(user_data)

    return render_template('Users/profile.html', user=user_data)




@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Sesión cerrada', 'info')
    return redirect(url_for('index'))

