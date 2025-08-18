from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app import app
import requests
from app.models.SearchFoodModel import save_food_entry, calculate_macros_for_quantity, get_food_entries_for_date
from datetime import date


@app.route('/search_food')
@login_required
def search_food():
    query = request.args.get('query', '').strip()

    # 🔹 Obtener alimentos registrados hoy
    today_foods = get_food_entries_for_date(current_user.id, date.today())

    if not query:        
        return render_template(
            "SearchFood/FoodResults.html",
            alimentos=[],
            query="",
            today_foods=today_foods
        )

    try:
        response = requests.get(
            "https://world.openfoodfacts.org/cgi/search.pl",
            params={
                'search_terms': query,
                'json': 1,
                'page_size': 100
            }
        )
        response.raise_for_status()
        data = response.json()
        productos = data.get("products", [])

        alimentos = []
        for prod in productos:
            product_code = prod.get('code')
            if product_code:
                alimentos.append({
                    'nombre': prod.get('product_name', 'Sin nombre'),
                    'calorias': prod.get('nutriments', {}).get('energy-kcal_100g', 'N/D'),
                    'proteinas': prod.get('nutriments', {}).get('proteins_100g', 'N/D'),
                    'grasas': prod.get('nutriments', {}).get('fat_100g', 'N/D'),
                    'carbohidratos': prod.get('nutriments', {}).get('carbohydrates_100g', 'N/D'),
                    'imagen': prod.get('image_front_small_url') or url_for('static', filename='default-food.jpg'),
                    'code': product_code
                })

        return render_template(
            'SearchFood/FoodResults.html',
            alimentos=alimentos,
            query=query,
            today_foods=today_foods
        )

    except requests.exceptions.RequestException as e:
        flash(f"Error de conexión al buscar alimentos: {str(e)}", "danger")
        return redirect(url_for('dashboard'))
    except Exception as e:
        flash(f"Error inesperado al buscar alimentos: {str(e)}", "danger")
        return redirect(url_for('dashboard'))



@app.route('/food_detail')
@login_required
def food_detail():
    product_code = request.args.get('code') 

    if not product_code:
        flash("Código de producto no proporcionado para el detalle.", "danger")
        return redirect(url_for('search_food'))

    try:
        response = requests.get(
            f"https://world.openfoodfacts.org/api/v0/product/{product_code}.json"
        )
        response.raise_for_status()
        data = response.json()
        product = data.get('product')

        if not product:
            flash("Producto no encontrado o datos incompletos.", "danger")
            return redirect(url_for('search_food'))

        nombre = product.get('product_name', 'Sin nombre')
        nutriments = product.get('nutriments', {})
        calorias = nutriments.get('energy-kcal_100g', 'N/D')
        proteinas = nutriments.get('proteins_100g', 'N/D')
        grasas = nutriments.get('fat_100g', 'N/D')
        carbohidratos = nutriments.get('carbohydrates_100g', 'N/D')
        imagen = product.get('image_front_small_url') or url_for('static', filename='default-food.jpg')

        return render_template('SearchFood/FoodDetail.html',
                               nombre=nombre,
                               calorias=calorias,
                               proteinas=proteinas,
                               grasas=grasas,
                               carbohidratos=carbohidratos,
                               imagen=imagen)

    except requests.exceptions.RequestException as e:
        flash(f"Error de conexión al obtener detalles del alimento: {str(e)}", "danger")
        return redirect(url_for('search_food'))
    except Exception as e:
        flash(f"Error inesperado al obtener detalles del alimento: {str(e)}", "danger")
        return redirect(url_for('search_food'))


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

   
    calories, proteins, fats, carbs = calculate_macros_for_quantity(
        calories_100g, proteins_100g, fats_100g, carbs_100g, quantity
    )

    try:
        save_food_entry(current_user.id, food_name, calories, proteins, fats, carbs)
        flash(f'"{food_name}" ({quantity} g) registrado correctamente', 'success')
    except Exception as e:
        flash(f'Error al guardar: {str(e)}', 'danger')

    return redirect(url_for('search_food'))

