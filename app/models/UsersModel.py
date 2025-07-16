from app.conexion import get_db_cursor

def get_user_profile(user_id):
    """
    Obtiene los datos del perfil del usuario desde la tabla loggin.
    Retorna un diccionario con los campos o None si no existe.
    """
    with get_db_cursor() as cursor:
        cursor.execute("""
            SELECT id, username, email, full_name, birth_date, height_cm, weight_kg, gender, activity_level, goal
            FROM loggin
            WHERE id = ?
        """, (user_id,))
        row = cursor.fetchone()
        if row is None:
            return None
        if not isinstance(row, dict):
            row = dict(row)
        return row


def update_user_profile(user_id, full_name, birth_date, height_cm, weight_kg, gender, activity_level, goal):
    """
    Actualiza los datos del perfil del usuario en la tabla loggin.
    """
    with get_db_cursor() as cursor:
        cursor.execute("""
            UPDATE loggin 
            SET full_name = ?, birth_date = ?, height_cm = ?, weight_kg = ?, gender = ?, activity_level = ?, goal = ?
            WHERE id = ?
        """, (full_name, birth_date, height_cm, weight_kg, gender, activity_level, goal, user_id))

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
