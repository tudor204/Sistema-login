from flask import render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from app import app
from app.conexion import get_db_cursor


@app.route('/mis-comidas')
@login_required
def mis_comidas():
    # Obtener todas las comidas del usuario ordenadas por fecha
    with get_db_cursor() as cur:
        cur.execute("""
            SELECT id, food_name, calories, proteins, date
            FROM food_entries
            WHERE user_id = ?
            ORDER BY date DESC
        """, (current_user.id,))
        comidas = cur.fetchall()
    
    return render_template('Myfoods/mis_comidas.html', comidas=comidas)

@app.route('/eliminar-comida/<int:comida_id>', methods=['POST'])
@login_required
def eliminar_comida(comida_id):
    with get_db_cursor() as cur:
        cur.execute("DELETE FROM food_entries WHERE id = ? AND user_id = ?", 
                   (comida_id, current_user.id))
    flash('Comida eliminada correctamente', 'success')
    return redirect(url_for('mis_comidas'))