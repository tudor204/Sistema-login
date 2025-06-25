from flask import render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user
from app import app, google
from app.models import User
import requests
from datetime import datetime
from app.conexion import get_db_cursor

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form.get('email')

        if not username or not password:
            flash('Usuario y contraseña son obligatorios', 'danger')
            return redirect(url_for('register'))

        try:
            with get_db_cursor() as cur:
                cur.execute("SELECT id FROM loggin WHERE username = ? OR email = ?", 
                          (username, email))
                if cur.fetchone():
                    flash('Usuario o email ya registrado', 'warning')
                    return redirect(url_for('register'))
                
                hashed_password = generate_password_hash(password)
                user_id = User.create(username, email, hashed_password)
                
                flash('Registro exitoso. Por favor inicia sesión', 'success')
                return redirect(url_for('login'))
        
        except Exception as e:
            flash(f'Error al registrar: {str(e)}', 'danger')
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        try:
            with get_db_cursor() as cur:
                cur.execute("SELECT * FROM loggin WHERE username = ?", (username,))
                user_data = cur.fetchone()

                if user_data and check_password_hash(user_data['password'], password):
                    user = User(id=user_data['id'], username=user_data['username'], 
                               email=user_data['email'])
                    login_user(user)
                    return redirect(url_for('dashboard'))
                
            flash('Credenciales inválidas', 'danger')
        
        except Exception as e:
            flash(f'Error al iniciar sesión: {str(e)}', 'danger')
    
    return render_template('login.html')

@app.route('/login/google')
def login_google():
    redirect_uri = url_for('authorize_google', _external=True)
    return google.authorize_redirect(redirect_uri)

@app.route('/authorize/google')
def authorize_google():
    claims_options = {
        "iss": {
            "values": ["https://accounts.google.com", "accounts.google.com"]
        }
    }
    token = google.authorize_access_token(claims_options=claims_options)
    resp = google.get('userinfo')
    user_info = resp.json()
    
    # Extraemos email y nombre
    email = user_info['email']
    username = user_info.get('name', email.split('@')[0])  # nombre o parte del email

    # Buscar usuario en BD por email
    user = User.get_by_email(email)
    
    if not user:
        # Crear usuario nuevo si no existe
        User.create(username, email)
        user = User.get_by_email(email)

    # Loguear usuario
    login_user(user)
    flash(f'Has iniciado sesión como {user.username} con Google', 'success')
    return redirect(url_for('dashboard'))

@app.route('/dashboard')
@login_required
def dashboard():
    with get_db_cursor() as cur:
        # Obtener metas del usuario
        cur.execute("SELECT * FROM user_goals WHERE user_id = ?", (current_user.id,))
        goals = cur.fetchone() or {'daily_calories': 2000, 'daily_proteins': 50, 'daily_water': 2}

        # Estadísticas de hoy
        cur.execute("""
            SELECT SUM(calories) as calories, SUM(proteins) as proteins
            FROM food_entries
            WHERE user_id = ? AND date(date) = date('now')
        """, (current_user.id,))
        today_stats = cur.fetchone() or {'calories': 0, 'proteins': 0}

        # Alimentos recientes
        cur.execute("""
            SELECT food_name, calories, proteins, date
            FROM food_entries
            WHERE user_id = ?
            ORDER BY date DESC
            LIMIT 5
        """, (current_user.id,))
        recent_foods = cur.fetchall()


    # Calcular porcentajes
    calories_percentage = min(100, (today_stats['calories'] or 0) / goals['daily_calories'] * 100)
    proteins_percentage = min(100, (today_stats['proteins'] or 0) / goals['daily_proteins'] * 100)

    return render_template('dashboard.html',
        goals=goals,
        today_stats=today_stats,
        recent_foods=recent_foods,
        calories_percentage=round(calories_percentage, 1),
        proteins_percentage=round(proteins_percentage, 1)
    )

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

        return render_template('food_results.html', alimentos=alimentos, query=query)

    except Exception as e:
        flash(f"Error al buscar alimentos: {str(e)}", "danger")
        return redirect(url_for('dashboard'))

@app.route('/save_food', methods=['POST'])
@login_required
def save_food():
    food_name = request.form.get('food_name')
    calories = request.form.get('calories', type=float)
    proteins = request.form.get('proteins', type=float)

    if not food_name or not calories:
        flash('Datos incompletos', 'warning')
        return redirect(url_for('search_food'))

    try:
        with get_db_cursor() as cur:
            cur.execute(
                "INSERT INTO food_entries (user_id, food_name, calories, proteins) VALUES (?, ?, ?, ?)",
                (current_user.id, food_name, calories, proteins)
            )
        flash(f'"{food_name}" registrado correctamente', 'success')
    except Exception as e:
        flash(f'Error al guardar: {str(e)}', 'danger')

    return redirect(url_for('dashboard'))

@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html')

@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    if request.method == 'POST':
        daily_calories = request.form.get('daily_calories', type=int)
        daily_proteins = request.form.get('daily_proteins', type=int)
        daily_water = request.form.get('daily_water', type=int)

        if not all([1000 <= daily_calories <= 5000, 
                   daily_proteins > 0, 
                   daily_water > 0]):
            flash('Valores inválidos', 'danger')
        else:
            with get_db_cursor() as cur:
                cur.execute("""
                    INSERT OR REPLACE INTO user_goals 
                    (user_id, daily_calories, daily_proteins, daily_water)
                    VALUES (?, ?, ?, ?)
                """, (current_user.id, daily_calories, daily_proteins, daily_water))
                flash('Configuración guardada', 'success')
    
    with get_db_cursor() as cur:
        cur.execute("SELECT * FROM user_goals WHERE user_id = ?", (current_user.id,))
        goals = cur.fetchone() or {'daily_calories': 2000, 'daily_proteins': 50, 'daily_water': 2}

    return render_template('settings.html', goals=goals)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Sesión cerrada', 'info')
    return redirect(url_for('index'))



@app.route('/mis-comidas')
@login_required
def mis_comidas():
    # Obtener todas las comidas del usuario ordenadas por fecha
    with get_db_cursor() as cur:
        cur.execute("""
            SELECT id, food_name, calories, proteins, date
            FROM food_entries
            WHERE user_id = ?
            ORDER BY date DESC
        """, (current_user.id,))
        comidas = cur.fetchall()
    
    return render_template('mis_comidas.html', comidas=comidas)

@app.route('/eliminar-comida/<int:comida_id>', methods=['POST'])
@login_required
def eliminar_comida(comida_id):
    with get_db_cursor() as cur:
        cur.execute("DELETE FROM food_entries WHERE id = ? AND user_id = ?", 
                   (comida_id, current_user.id))
    flash('Comida eliminada correctamente', 'success')
    return redirect(url_for('mis_comidas'))

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
    
    return render_template('progreso.html', 
                         datos_calorias=datos_calorias,
                         macros=macros)