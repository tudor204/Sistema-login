from flask import render_template, request, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user
from app import app, google
from app.models.LoginGoogleModel import User
from app.conexion import get_db_cursor

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
    
    return render_template('LoginGoogle/register.html')

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
    
    return render_template('LoginGoogle/login.html')

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