# rutas relacionadas con comidas
from flask import render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from app import app
from datetime import date
from app.models.MyFoodModel import (
    get_comidas_by_user, delete_comida,
    get_comida_by_id, update_comida,
    get_totales_diarios
)
from datetime import datetime


@app.route('/mis-comidas')
@login_required
def mis_comidas():
    try:
        # Histórico completo de comidas
        comidas = get_comidas_by_user(current_user.id)

        # Totales solo de hoy
        totales = get_totales_diarios(current_user.id)

    except Exception as e:
        current_app.logger.exception("Error al obtener comidas: %s", e)
        flash("Error al cargar tus comidas. Intenta de nuevo más tarde.", "danger")
        comidas = []
        totales = {"total_calorias": 0, "total_proteinas": 0}

    return render_template(
        'Myfoods/mis_comidas.html',
        comidas=comidas,
        total_calorias=totales["total_calorias"],
        total_proteinas=totales["total_proteinas"]
    )

@app.route('/comidas/eliminar/<int:comida_id>', methods=['POST'])
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

@app.route('/comidas/editar/<int:comida_id>', methods=['GET', 'POST'])
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
        fats = request.form.get('fats', '').strip()
        carbs = request.form.get('carbs', '').strip()
        date_iso = request.form.get('date', '').strip()

        errors = []
        # Validaciones básicas
        if not food_name:
            errors.append("El nombre del alimento no puede estar vacío.")

        def validar_float(valor, nombre):
            try:
                val = float(valor)
                if val < 0:
                    errors.append(f"{nombre} no pueden ser negativos.")
                return val
            except ValueError:
                errors.append(f"Introduce un número válido para {nombre.lower()}.")
                return None

        calories_val = validar_float(calories, "Calorías")
        proteins_val = validar_float(proteins, "Proteínas")
        fats_val = validar_float(fats, "Grasas")
        carbs_val = validar_float(carbs, "Carbohidratos")

        try:
            datetime.strptime(date_iso, '%Y-%m-%d')
        except ValueError:
            errors.append("Fecha inválida. Usa el selector de fecha.")

        if errors:
            for e in errors:
                flash(e, 'danger')
            # 👇 En modal, simplemente rediriges de nuevo a mis_comidas
            return redirect(url_for('mis_comidas'))

        try:
            updated = update_comida(
                current_user.id, comida_id,
                food_name, calories_val, proteins_val,
                fats_val, carbs_val, date_iso
            )
            if updated:
                flash('Comida actualizada correctamente.', 'success')
            else:
                flash('No se pudo actualizar la comida (puede que no exista).', 'warning')
        except Exception as e:
            current_app.logger.exception("Error al actualizar comida: %s", e)
            flash('Error al actualizar la comida.', 'danger')

        return redirect(url_for('mis_comidas'))

    # Si accedes por GET, sigues mostrando la plantilla standalone
    return render_template('Myfoods/editar_comida.html', comida=comida)

#Agregar comida manualmente

@app.route('/agregar-comida', methods=['GET', 'POST'])
@login_required
def agregar_comida_route():
    today_str = date.today().strftime('%Y-%m-%d')  # Definimos hoy al inicio
    if request.method == 'POST':
        food_name = request.form.get('food_name', '').strip()
        calories = request.form.get('calories', '').strip()
        proteins = request.form.get('proteins', '').strip()
        fats = request.form.get('fats', '').strip()
        carbs = request.form.get('carbs', '').strip()
        date_iso = request.form.get('date', '').strip()

        errors = []
        if not food_name:
            errors.append("El nombre del alimento no puede estar vacío.")

        try:
            calories_val = float(calories)
            if calories_val < 0: errors.append("Las calorías no pueden ser negativas.")
        except ValueError:
            errors.append("Introduce un número válido para las calorías.")

        try:
            proteins_val = float(proteins)
            if proteins_val < 0: errors.append("Las proteínas no pueden ser negativas.")
        except ValueError:
            errors.append("Introduce un número válido para las proteínas.")

        try:
            fats_val = float(fats)
            if fats_val < 0: errors.append("Las grasas no pueden ser negativas.")
        except ValueError:
            errors.append("Introduce un número válido para las grasas.")

        try:
            carbs_val = float(carbs)
            if carbs_val < 0: errors.append("Los carbohidratos no pueden ser negativos.")
        except ValueError:
            errors.append("Introduce un número válido para los carbohidratos.")

        try:
            datetime.strptime(date_iso, '%Y-%m-%d')
        except ValueError:
            errors.append("Fecha inválida. Usa el selector de fecha.")

        if errors:
            for e in errors: flash(e, 'danger')
            # Pasamos `today` también en caso de error
            return render_template('Myfoods/AgregarComida.html', today=today_str)

        from app.models.MyFoodModel import create_comida
        created_id = create_comida(current_user.id, food_name, calories_val, proteins_val, fats_val, carbs_val, date_iso)
        if created_id:
            flash("Comida agregada correctamente.", "success")
        else:
            flash("No se pudo agregar la comida.", "danger")
        return redirect(url_for('mis_comidas'))

    # GET → mostrar formulario vacío
    return render_template('Myfoods/AgregarComida.html', today=today_str)


@app.route('/comidas/duplicar/<int:comida_id>', methods=['POST'])
@login_required
def duplicar_comida_route(comida_id):
    try:
        comida = get_comida_by_id(current_user.id, comida_id)
        if not comida:
            flash('Comida no encontrada.', 'warning')
            return redirect(url_for('mis_comidas'))

        from datetime import date
        fecha_nueva = request.form.get('date', date.today().strftime('%Y-%m-%d'))

        try:
            datetime.strptime(fecha_nueva, '%Y-%m-%d')
        except ValueError:
            flash('Fecha inválida.', 'danger')
            return redirect(url_for('mis_comidas'))

        from app.models.MyFoodModel import create_comida
        nueva_comida_id = create_comida(
            user_id=current_user.id,
            food_name=comida['food_name'],
            calories=float(comida['calories']),
            proteins=float(comida['proteins']),
            fats=float(comida['fats']),
            carbs=float(comida['carbs']),
            date_iso=fecha_nueva
        )

        if nueva_comida_id:
            fecha_display = datetime.strptime(fecha_nueva, '%Y-%m-%d').strftime('%d/%m/%Y')
            flash(f'"{comida["food_name"]}" añadido para el {fecha_display}.', 'success')
        else:
            flash('No se pudo duplicar la comida.', 'danger')

    except Exception as e:
        current_app.logger.exception("Error al duplicar comida: %s", e)
        flash('Error al duplicar la comida.', 'danger')

    return redirect(url_for('mis_comidas'))
