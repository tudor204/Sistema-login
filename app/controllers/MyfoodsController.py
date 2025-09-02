# rutas relacionadas con comidas
from flask import render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from app import app
from app.models.MyFoodModel import (
    get_comidas_by_user, delete_comida,
    get_comida_by_id, update_comida
)
from datetime import datetime

@app.route('/mis-comidas')
@login_required
def mis_comidas():
    try:
        comidas = get_comidas_by_user(current_user.id)
    except Exception as e:
        current_app.logger.exception("Error al obtener comidas: %s", e)
        flash("Error al cargar tus comidas. Intenta de nuevo más tarde.", "danger")
        comidas = []

    # Sumar con tolerancia por si valores vienen como strings o None
    total_calorias = sum(float(c.get('calories') or 0) for c in comidas)
    total_proteinas = sum(float(c.get('proteins') or 0) for c in comidas)

    return render_template(
        'Myfoods/mis_comidas.html',
        comidas=comidas,
        total_calorias=int(total_calorias),
        total_proteinas=int(total_proteinas)
    )

@app.route('/eliminar-comida/<int:comida_id>', methods=['POST'])
@login_required
def eliminar_comida_route(comida_id):
    try:
        deleted = delete_comida(current_user.id, comida_id)
    except Exception as e:
        current_app.logger.exception("Error al eliminar comida: %s", e)
        flash("Error al eliminar la comida. Intenta de nuevo.", "danger")
        return redirect(url_for('mis_comidas'))

    if deleted:
        flash('Comida eliminada correctamente.', 'success')
    else:
        flash('No se encontró la comida o no tienes permiso para eliminarla.', 'warning')
    return redirect(url_for('mis_comidas'))

@app.route('/editar-comida/<int:comida_id>', methods=['GET', 'POST'])
@login_required
def editar_comida_route(comida_id):
    comida = get_comida_by_id(current_user.id, comida_id)
    if not comida:
        flash('Comida no encontrada.', 'warning')
        return redirect(url_for('mis_comidas'))

    if request.method == 'POST':
        food_name = request.form.get('food_name', '').strip()
        calories = request.form.get('calories', '').strip()
        proteins = request.form.get('proteins', '').strip()
        date_iso = request.form.get('date', '').strip()

        errors = []
        if not food_name:
            errors.append("El nombre del alimento no puede estar vacío.")
        try:
            calories_val = float(calories)
            if calories_val < 0:
                errors.append("Las calorías no pueden ser negativas.")
        except ValueError:
            errors.append("Introduce un número válido para las calorías.")
        try:
            proteins_val = float(proteins)
            if proteins_val < 0:
                errors.append("Las proteínas no pueden ser negativas.")
        except ValueError:
            errors.append("Introduce un número válido para las proteínas.")
        try:
            datetime.strptime(date_iso, '%Y-%m-%d')
        except ValueError:
            errors.append("Fecha inválida. Usa el selector de fecha.")

        if errors:
            for e in errors:
                flash(e, 'danger')
            # Renderizar de nuevo con los datos que envió el usuario
            comida_tmp = {
                'id': comida_id,
                'food_name': food_name,
                'calories': calories,
                'proteins': proteins,
                'date_iso': date_iso,
                'date': datetime.strptime(date_iso, '%Y-%m-%d').strftime('%d/%m/%Y') if date_iso else comida['date']
            }
            return render_template('Myfoods/editar_comida.html', comida=comida_tmp)

        try:
            updated = update_comida(current_user.id, comida_id, food_name, calories_val, proteins_val, date_iso)
            if updated:
                flash('Comida actualizada correctamente.', 'success')
            else:
                flash('No se pudo actualizar la comida (puede que no exista).', 'warning')
        except Exception as e:
            current_app.logger.exception("Error al actualizar comida: %s", e)
            flash('Error al actualizar la comida.', 'danger')

        return redirect(url_for('mis_comidas'))

    # GET -> mostrar formulario
    return render_template('Myfoods/editar_comida.html', comida=comida)

@app.route('/agregar-comida', methods=['GET', 'POST'])
@login_required
def agregar_comida_route():
    if request.method == 'POST':
        food_name = request.form.get('food_name', '').strip()
        calories = request.form.get('calories', '').strip()
        proteins = request.form.get('proteins', '').strip()
        date_iso = request.form.get('date', '').strip()
        

        errors = []
        if not food_name:
            errors.append("El nombre del alimento no puede estar vacío.")
        try:
            calories_val = float(calories)
            if calories_val < 0:
                errors.append("Las calorías no pueden ser negativas.")
        except ValueError:
            errors.append("Introduce un número válido para las calorías.")
        try:
            proteins_val = float(proteins)
            if proteins_val < 0:
                errors.append("Las proteínas no pueden ser negativas.")
        except ValueError:
            errors.append("Introduce un número válido para las proteínas.")
        try:
            datetime.strptime(date_iso, '%Y-%m-%d')
        except ValueError:
            errors.append("Fecha inválida. Usa el selector de fecha.")

        if errors:
            for e in errors:
                flash(e, 'danger')
            return render_template('Myfoods/agregar_comida.html')

        from app.models.MyFoodModel import create_comida
        created_id = create_comida(current_user.id, food_name, calories_val, proteins_val, date_iso)
        if created_id:
            flash("Comida agregada correctamente.", "success")
        else:
            flash("No se pudo agregar la comida.", "danger")
        return redirect(url_for('mis_comidas'))

    return render_template('Myfoods/AgregarComida.html')


# Añadir esta ruta a tu archivo de rutas existente

@app.route('/duplicar-comida/<int:comida_id>', methods=['POST'])
@login_required
def duplicar_comida_route(comida_id):
    """Duplica una comida existente y la añade con la fecha de hoy."""
    try:
        # Obtener los datos de la comida original
        comida = get_comida_by_id(current_user.id, comida_id)
        
        if not comida:
            flash('Comida no encontrada.', 'warning')
            return redirect(url_for('mis_comidas'))
        
        # Obtener la fecha del formulario o usar hoy por defecto
        from datetime import date
        fecha_nueva = request.form.get('date', date.today().strftime('%Y-%m-%d'))
        
        # Validar la fecha
        try:
            datetime.strptime(fecha_nueva, '%Y-%m-%d')
        except ValueError:
            flash('Fecha inválida.', 'danger')
            return redirect(url_for('mis_comidas'))
        
        # Crear la nueva entrada duplicando los datos
        from app.models.MyFoodModel import create_comida
        nueva_comida_id = create_comida(
            user_id=current_user.id,
            food_name=comida['food_name'],
            calories=float(comida['calories']),
            proteins=float(comida['proteins']),
            date_iso=fecha_nueva
        )
        
        if nueva_comida_id:
            # Formatear la fecha para mostrar
            fecha_display = datetime.strptime(fecha_nueva, '%Y-%m-%d').strftime('%d/%m/%Y')
            flash(f'"{comida["food_name"]}" añadido para el {fecha_display}.', 'success')
        else:
            flash('No se pudo duplicar la comida.', 'danger')
            
    except Exception as e:
        current_app.logger.exception("Error al duplicar comida: %s", e)
        flash('Error al duplicar la comida.', 'danger')
    
    return redirect(url_for('mis_comidas'))

