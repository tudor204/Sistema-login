from flask import render_template, request, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user
from app import app, google
from app.models.LoginGoogleModel import User, UserExistsError
from app.conexion import get_db_cursor
from app.models.SettingsModel import get_user_goals

def user_has_settings(user_id):
    goals = get_user_goals(user_id)
    return goals.get('weight') and goals.get('height')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form.get('email')

        if not username or not password or not email: # Asegurar que email también sea obligatorio
            flash('Usuario, email y contraseña son obligatorios', 'danger')
            return redirect(url_for('register'))

        try:
            # 1. CENTRALIZACIÓN DE LA LÓGICA: Llama al modelo para verificar duplicados
            User.check_for_duplicates(username, email) 
            
            # 2. Si no hay excepción (no hay duplicados), procedemos a crear
            hashed_password = generate_password_hash(password)
            user_id = User.create(username, email, hashed_password)
            
            flash('Registro exitoso. Por favor, inicia sesión', 'success')
            return redirect(url_for('login'))
        
        except UserExistsError as e:
            # 3. Captura la excepción específica y notifica al usuario
            flash(str(e), 'warning') # str(e) contiene el mensaje detallado (Ej: "El email ya está en uso.")
            return redirect(url_for('register'))
            
        except Exception as e:
            # 4. Captura cualquier otro error (problemas de conexión, etc.)
            flash(f'Error al registrar: {str(e)}', 'danger')
            return render_template('LoginGoogle/register.html')
            
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
                    if user_has_settings(user.id):
                        return redirect(url_for('dashboard'))
                    else:
                        return redirect(url_for('settings'))

                
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
       
  
    token = google.authorize_access_token()   
    user_info = token.get('userinfo')
    
    if not user_info:
       
        resp = google.get('userinfo')
        resp.raise_for_status() 
        user_info = resp.json()

    email = user_info['email']    
    username = user_info.get('name', email.split('@')[0])
    
    # Busca al usuario en tu base de datos por su email
    user = User.get_by_email(email)
    
    if not user:
        # Si el usuario no existe, lo creamos
        # Asegúrate de que User.create maneje el caso de google_id
        user_id = User.create(username=username, email=email, google_id=user_info.get('sub'))
        user = User.get_by_id(user_id) # Obtenemos el objeto User recién creado

    # Inicia sesión con el usuario (existente o nuevo)
    if user:
        login_user(user)
        flash(f'Has iniciado sesión como {user.username} con Google', 'success')
        
        if user_has_settings(user.id):
            return redirect(url_for('dashboard'))
        else:
            return redirect(url_for('settings'))
    else:
        flash('Hubo un error al intentar iniciar sesión con Google.', 'danger')
        return redirect(url_for('login'))


