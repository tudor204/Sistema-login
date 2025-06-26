from flask import render_template
from flask_login import login_required, current_user
from app import app
from app.conexion import get_db_cursor

@app.route('/progreso')
@login_required
def progreso():
    # Obtener datos para gráficos (últimos 7 días)
    with get_db_cursor() as cur:
        # Datos de calorías diarias - convertimos a lista de diccionarios
        cur.execute("""
            SELECT date(date) as dia, SUM(calories) as total_calorias
            FROM food_entries
            WHERE user_id = ? AND date >= date('now', '-7 days')
            GROUP BY dia
            ORDER BY dia
        """, (current_user.id,))
        datos_calorias = [dict(row) for row in cur.fetchall()]
        
        # Datos de macronutrientes - convertimos a diccionario
        cur.execute("""
            SELECT SUM(proteins) as proteinas, 
                   SUM(fats) as grasas, 
                   SUM(carbs) as carbohidratos
            FROM food_entries
            WHERE user_id = ? AND date >= date('now', '-7 days')
        """, (current_user.id,))
        macros = dict(cur.fetchone()) or {'proteinas': 0, 'grasas': 0, 'carbohidratos': 0}
    
    return render_template('Progress/progreso.html', 
                         datos_calorias=datos_calorias,
                         macros=macros)