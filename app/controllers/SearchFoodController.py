from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app import app
import requests
from app.models.SearchFoodModel import save_food_entry, calculate_macros_for_quantity


@app.route('/search_food')
@login_required
def search_food():
    query = request.args.get('query', '').strip()
    if not query:
        flash("Ingresa un alimento para buscar", "warning")
        return render_template("SearchFood/FoodResults.html", alimentos=[], query="")

    try:
        response = requests.get(
            "https://world.openfoodfacts.org/cgi/search.pl",
            params={
                'search_terms': query,
                'json': 1,
                'page_size': 10
            }
        )
        data = response.json()
        productos = data.get("products", [])

        alimentos = []
        for prod in productos:
            alimentos.append({
                'nombre': prod.get('product_name', 'Sin nombre'),
                'calorias': prod.get('nutriments', {}).get('energy-kcal_100g', 'N/D'),
                'proteinas': prod.get('nutriments', {}).get('proteins_100g', 'N/D'),
                'grasas': prod.get('nutriments', {}).get('fat_100g', 'N/D'),
                'carbohidratos': prod.get('nutriments', {}).get('carbohydrates_100g', 'N/D'),
                'imagen': prod.get('image_front_small_url') or '/static/default-food.jpg'
            })

        return render_template('SearchFood/FoodResults.html', alimentos=alimentos, query=query)

    except Exception as e:
        flash(f"Error al buscar alimentos: {str(e)}", "danger")
        return redirect(url_for('dashboard'))


@app.route('/food_detail')
@login_required
def food_detail():
    nombre = request.args.get('nombre')
    calorias = request.args.get('calorias')
    proteinas = request.args.get('proteinas')
    grasas = request.args.get('grasas')
    carbohidratos = request.args.get('carbohidratos')
    imagen = request.args.get('imagen', '/static/default-food.jpg')

    return render_template('SearchFood/FoodDetail.html',
                        nombre=nombre,
                        calorias=calorias,
                        proteinas=proteinas,
                        grasas=grasas,
                        carbohidratos=carbohidratos,
                        imagen=imagen)


@app.route('/save_food', methods=['POST'])
@login_required
def save_food():
    food_name = request.form.get('food_name')
    calories_100g = request.form.get('calories_per_100g', type=float)
    proteins_100g = request.form.get('proteins_per_100g', type=float)
    fats_100g = request.form.get('fats_per_100g', type=float, default=0)
    carbs_100g = request.form.get('carbs_per_100g', type=float, default=0)
    quantity = request.form.get('quantity', type=float) or 100

    if not food_name or calories_100g is None or proteins_100g is None:
        flash('Datos incompletos', 'warning')
        return redirect(url_for('search_food'))

    calories = round(calories_100g * quantity / 100, 2)
    proteins = round(proteins_100g * quantity / 100, 2)
    fats = round(fats_100g * quantity / 100, 2)
    carbs = round(carbs_100g * quantity / 100, 2)

    try:
        save_food_entry(food_name, calories, proteins, fats, carbs)
        flash(f'"{food_name}" ({quantity} g) registrado correctamente', 'success')
    except Exception as e:
        flash(f'Error al guardar: {str(e)}', 'danger')

    return redirect(url_for('dashboard'))
