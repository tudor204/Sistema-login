from app.conexion import get_db_cursor
from werkzeug.security import check_password_hash, generate_password_hash
import json

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_user_profile(user_id):
    with get_db_cursor() as cursor:
        cursor.execute("""
            SELECT username, email, full_name, birth_date, height_cm, weight_kg, gender, activity_level, goal, profile_photo
            FROM loggin WHERE id = ?
        """, (user_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

def update_user_profile(user_id, full_name, birth_date, height_cm, weight_kg, gender, activity_level, goal, profile_photo=None):
    with get_db_cursor() as cursor:
        if profile_photo:
            cursor.execute("""
                UPDATE loggin SET full_name=?, birth_date=?, height_cm=?, weight_kg=?, gender=?, activity_level=?, goal=?, profile_photo=?
                WHERE id=?
            """, (full_name, birth_date, height_cm, weight_kg, gender, activity_level, goal, profile_photo, user_id))
        else:
            cursor.execute("""
                UPDATE loggin SET full_name=?, birth_date=?, height_cm=?, weight_kg=?, gender=?, activity_level=?, goal=?
                WHERE id=?
            """, (full_name, birth_date, height_cm, weight_kg, gender, activity_level, goal, user_id))

def update_user_preferences(user_id, preferences_dict):
    with get_db_cursor() as cursor:
        cursor.execute("""
            UPDATE loggin SET preferences=? WHERE id=?
        """, (json.dumps(preferences_dict), user_id))

def get_user_preferences(user_id):
    with get_db_cursor() as cursor:
        cursor.execute("SELECT preferences FROM loggin WHERE id = ?", (user_id,))
        row = cursor.fetchone()
        try:
            return json.loads(row["preferences"]) if row and row["preferences"] else {}
        except:
            return {}

def check_user_password(user_id, password):
    with get_db_cursor() as cursor:
        cursor.execute("SELECT password FROM loggin WHERE id = ?", (user_id,))
        row = cursor.fetchone()
        return row and check_password_hash(row["password"], password)

def update_user_password(user_id, new_password):
    hashed_pw = generate_password_hash(new_password)
    with get_db_cursor() as cursor:
        cursor.execute("UPDATE loggin SET password = ? WHERE id = ?", (hashed_pw, user_id))

def check_email_exists(email, exclude_user_id):
    with get_db_cursor() as cursor:
        cursor.execute("SELECT id FROM loggin WHERE email = ? AND id != ?", (email, exclude_user_id))
        return cursor.fetchone() is not None

def update_user_email(user_id, new_email):
    with get_db_cursor() as cursor:
        cursor.execute("UPDATE loggin SET email = ? WHERE id = ?", (new_email, user_id))

def delete_user_account(user_id):
    with get_db_cursor() as cursor:
        cursor.execute("DELETE FROM loggin WHERE id = ?", (user_id,))
