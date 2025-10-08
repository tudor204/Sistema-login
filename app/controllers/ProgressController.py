from flask import render_template
from flask_login import login_required, current_user
from app import app
from app.conexion import get_db_cursor
from app.models.ProgressModel import obtener_dias_registrados, obtener_resumen_dia
import datetime


@app.route('/progreso')
@app.route('/progreso/<fecha>')
@login_required
def progreso(fecha=None):
    # Usar día actual si no se especifica fecha
    if not fecha:
        fecha = datetime.date.today().isoformat()
    
    # Convertir fecha string a objeto datetime.date
    try:
        fecha_obj = datetime.datetime.strptime(fecha, '%Y-%m-%d').date()
    except ValueError:
        # En caso de que el formato no sea válido, usar hoy
        fecha_obj = datetime.date.today()
        fecha = fecha_obj.isoformat()

    with get_db_cursor() as cur:
        # Calorías consumidos 7 días relativos a la fecha seleccionada
        cur.execute("""
            SELECT date(date) AS dia, SUM(calories) AS total_calorias
            FROM food_entries
            WHERE user_id = ? AND date BETWEEN date(?, '-6 days') AND ?
            GROUP BY dia
            ORDER BY dia
        """, (current_user.id, fecha, fecha))
        datos_calorias = [dict(row) for row in (cur.fetchall() or [])]

        # Macronutrientes sumados para los 7 días relativos a la fecha seleccionada
        cur.execute("""
            SELECT 
                COALESCE(SUM(proteins), 0) AS proteinas, 
                COALESCE(SUM(fats), 0) AS grasas, 
                COALESCE(SUM(carbs), 0) AS carbohidratos
            FROM food_entries
            WHERE user_id = ? AND date BETWEEN date(?, '-6 days') AND ?
        """, (current_user.id, fecha, fecha))
        row = cur.fetchone()
        macros = dict(row) if row else {'proteinas': 0, 'grasas': 0, 'carbohidratos': 0}

    dias_disponibles = obtener_dias_registrados(current_user.id)
    resumen_dia = obtener_resumen_dia(current_user.id, fecha)

    return render_template('Progress/progreso.html',
                           datos_calorias=datos_calorias,
                           macros=macros,
                           dias_disponibles=dias_disponibles,
                           resumen_dia=resumen_dia,
                           fecha_seleccionada=fecha,
                           fecha_obj=fecha_obj)