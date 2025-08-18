from flask import render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from app import app
from app.models.MyFoodModel import get_comidas_by_user, delete_comida
from datetime import datetime

@app.route('/mis-comidas')
@login_required
def mis_comidas():
    comidas_raw = get_comidas_by_user(current_user.id)

    # Convertir sqlite3.Row a diccionario y parsear fechas
    comidas = []
    for comida in comidas_raw:
        comida_dict = dict(comida)
        # Convierte a datetime y formatea como string dd/mm/yyyy
        comida_dict['date'] = datetime.strptime(comida_dict['date'], '%Y-%m-%d').strftime('%d/%m/%Y')
        comidas.append(comida_dict)
        

    # Calcular totales
    total_calorias = sum(comida['calories'] for comida in comidas)
    total_proteinas = sum(comida['proteins'] for comida in comidas)

    return render_template(
        'Myfoods/mis_comidas.html',
        comidas=comidas,
        total_calorias=total_calorias,
        total_proteinas=total_proteinas
    )

@app.route('/eliminar-comida/<int:comida_id>', methods=['POST'])
@login_required
def eliminar_comida_route(comida_id):
    delete_comida(current_user.id, comida_id)
    flash('Comida eliminada correctamente', 'success')
    return redirect(url_for('mis_comidas'))

