from flask import render_template
from flask_login import login_required, current_user
from app import app
from app.models.ProgressModel import (
    obtener_dias_registrados, 
    obtener_resumen_dia, 
    obtener_datos_calorias_7dias, 
    obtener_macros_totales_7dias,
    obtener_metas_nutricionales # Nueva función
)
import datetime


@app.route('/progreso')
@app.route('/progreso/<fecha>')
@login_required
def progreso(fecha=None):
    # --- 1. Gestión de Fecha ---
    if not fecha:
        fecha = datetime.date.today().isoformat()
    
    try:
        fecha_obj = datetime.datetime.strptime(fecha, '%Y-%m-%d').date()
    except ValueError:
        # En caso de que el formato no sea válido, usar hoy
        fecha_obj = datetime.date.today()
        fecha = fecha_obj.isoformat()

    user_id = current_user.id
    
    # --- 2. Llamadas al Modelo (Acceso a Datos Centralizado) ---
    
    # Datos para el gráfico de 7 días
    datos_calorias_7dias = obtener_datos_calorias_7dias(user_id, fecha)
    
    # Datos generales (macros totales de 7 días - menos útil, pero se mantiene si es necesario)
    macros_totales_7dias = obtener_macros_totales_7dias(user_id, fecha)
    
    # Resumen detallado del día seleccionado
    resumen_dia = obtener_resumen_dia(user_id, fecha)
    
    # Días disponibles para la navegación lateral (más intuitivo)
    dias_disponibles = obtener_dias_registrados(user_id)

    # Metas (Necesario para el nuevo gráfico de donut Intake vs Goal)
    metas = obtener_metas_nutricionales(user_id) # Usamos una función simulada en el modelo

    # --- 3. Renderización de la Vista ---
    return render_template('Progress/progreso.html',
                            datos_calorias=datos_calorias_7dias,
                            macros_totales=macros_totales_7dias,
                            dias_disponibles=dias_disponibles,
                            resumen_dia=resumen_dia,
                            metas=metas,
                            fecha_seleccionada=fecha,
                            fecha_obj=fecha_obj)
