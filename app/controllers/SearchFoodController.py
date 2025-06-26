from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app import app
import requests
from app.models.SearchFoodModel import save_food_entry 


@app.route('/search_food')
@login_required
def search_food():
    query = request.args.get('query', '').strip()
    if not query:
        flash("Ingresa un alimento para buscar", "warning")
        return redirect(url_for('dashboard'))

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
                'carbohidratos': prod.get('nutriments', {}).get('carbohydrates_100g', 'N/D')
            })

        return render_template('SearchFood/food_results.html', alimentos=alimentos, query=query)

    except Exception as e:
        flash(f"Error al buscar alimentos: {str(e)}", "danger")
        return redirect(url_for('dashboard'))

@app.route('/save_food', methods=['POST'])
@login_required
def save_food():
    food_name = request.form.get('food_name')
    calories = request.form.get('calories', type=float)
    proteins = request.form.get('proteins', type=float)

    if not food_name or calories is None:
        flash('Datos incompletos', 'warning')
        return redirect(url_for('search_food'))

    try:
        save_food_entry(food_name, calories, proteins)
        flash(f'"{food_name}" registrado correctamente', 'success')
    except Exception as e:
        flash(f'Error al guardar: {str(e)}', 'danger')

    return redirect(url_for('dashboard'))