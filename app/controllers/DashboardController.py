from flask import render_template, request,flash
from flask_login import login_required, current_user
from app import app
from app.conexion import get_db_cursor


@app.route('/dashboard')
@login_required
def dashboard():
    with get_db_cursor() as cur:
        # Obtener metas del usuario
        cur.execute("SELECT * FROM user_goals WHERE user_id = ?", (current_user.id,))
        goals = cur.fetchone() or {'daily_calories': 2000, 'daily_proteins': 50, 'daily_water': 2}

        # Estadísticas de hoy
        cur.execute("""
            SELECT SUM(calories) as calories, SUM(proteins) as proteins
            FROM food_entries
            WHERE user_id = ? AND date(date) = date('now')
        """, (current_user.id,))
        today_stats = cur.fetchone() or {'calories': 0, 'proteins': 0}

        # Alimentos recientes
        cur.execute("""
            SELECT food_name, calories, proteins, date
            FROM food_entries
            WHERE user_id = ?
            ORDER BY date DESC
            LIMIT 5
        """, (current_user.id,))
        recent_foods = cur.fetchall()


    # Calcular porcentajes
    calories_percentage = min(100, (today_stats['calories'] or 0) / goals['daily_calories'] * 100)
    proteins_percentage = min(100, (today_stats['proteins'] or 0) / goals['daily_proteins'] * 100)

    return render_template('Dashboard/dashboard.html',
        goals=goals,
        today_stats=today_stats,
        recent_foods=recent_foods,
        calories_percentage=round(calories_percentage, 1),
        proteins_percentage=round(proteins_percentage, 1)
    )

@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    if request.method == 'POST':
        daily_calories = request.form.get('daily_calories', type=int)
        daily_proteins = request.form.get('daily_proteins', type=int)
        daily_water = request.form.get('daily_water', type=int)

        if not all([1000 <= daily_calories <= 5000, 
                   daily_proteins > 0, 
                   daily_water > 0]):
            flash('Valores inválidos', 'danger')
        else:
            with get_db_cursor() as cur:
                cur.execute("""
                    INSERT OR REPLACE INTO user_goals 
                    (user_id, daily_calories, daily_proteins, daily_water)
                    VALUES (?, ?, ?, ?)
                """, (current_user.id, daily_calories, daily_proteins, daily_water))
                flash('Configuración guardada', 'success')
    
    with get_db_cursor() as cur:
        cur.execute("SELECT * FROM user_goals WHERE user_id = ?", (current_user.id,))
        goals = cur.fetchone() or {'daily_calories': 2000, 'daily_proteins': 50, 'daily_water': 2}

    return render_template('Dashboard/settings.html', goals=goals)