from flask import render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from app import app
from app.conexion import Conexion
import requests

@app.route ('/')
def index():
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Verificar si el usuario ya existe
        check_query = "SELECT * FROM loggin WHERE username = ?"
        try:
            check = Conexion(check_query, (username,))
            existing_user = check.fetch_all()
            check.close()

            if existing_user:
                flash('El nombre de usuario ya está registrado.', 'warning')
                return redirect(url_for('register'))

            # Si no existe, lo registramos
            hashed_password = generate_password_hash(password)
            insert_query = "INSERT INTO loggin (username, password) VALUES (?, ?)"
            con = Conexion(insert_query, (username, hashed_password))
            con.close()
            flash('Usuario registrado correctamente', 'success')
        except Exception as e:
            flash(f'Error al registrar usuario: {str(e)}', 'danger')

        return redirect(url_for('register'))

    return render_template('register.html')



@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password_input = request.form['password']

        query = "SELECT * FROM loggin WHERE username = ?"
        try:
            con = Conexion(query, (username,))
            user = con.res.fetchone()
            con.close()

            if user and check_password_hash(user[2], password_input):
                session['user_id'] = user[0]
                session['username'] = user[1]
                return redirect(url_for('dashboard'))
            else:
                flash('Credenciales inválidas.', 'danger')
        except Exception as e:
            flash(f'Error al iniciar sesión: {str(e)}', 'danger')

    return render_template('login.html')


@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html', username=session['username'])


@app.route('/logout')
def logout():
    session.clear()
    flash('Sesión cerrada.', 'info')
    return redirect(url_for('login'))




@app.route('/search_food')
def search_food():
    query = request.args.get('query')

    if not query:
        flash("Escribe un alimento para buscar", "warning")
        return redirect(url_for('dashboard'))

    # Llamada a OpenFoodFacts
    url = f"https://world.openfoodfacts.org/cgi/search.pl"
    params = {
        'search_terms': query,
        'search_simple': 1,
        'action': 'process',
        'json': 1,
    }

    try:
        response = requests.get(url, params=params)
        data = response.json()
        productos = data.get("products", [])[:10]  # Limita a 10 resultados

        # Procesar los productos para mostrar solo algunos campos
        alimentos = []
        for prod in productos:
            alimentos.append({
                'nombre': prod.get('product_name', 'Sin nombre'),
                'calorias': prod.get('nutriments', {}).get('energy-kcal_100g', 'N/D'),
                'proteinas': prod.get('nutriments', {}).get('proteins_100g', 'N/D'),
                'grasas': prod.get('nutriments', {}).get('fat_100g', 'N/D'),
                'carbohidratos': prod.get('nutriments', {}).get('carbohydrates_100g', 'N/D')
            })

        return render_template('food_results.html', alimentos=alimentos, query=query)

    except Exception as e:
        flash(f"Error al buscar alimentos: {str(e)}", "danger")
        return redirect(url_for('dashboard'))
