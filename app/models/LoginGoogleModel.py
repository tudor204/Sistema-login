from flask_login import UserMixin
from app.conexion import get_db_cursor

class User(UserMixin):
    def __init__(self, id, username, email=None, google_id=None, profile_photo=None):
        self.id = id
        self.username = username
        self.email = email
        self.google_id = google_id
        self.profile_photo = profile_photo


    @staticmethod
    def get_by_id(user_id):
        with get_db_cursor() as cur:
            cur.execute("SELECT * FROM loggin WHERE id = ?", (user_id,))
            user = cur.fetchone()
            if user:
                return User(
                    id=user['id'],
                    username=user['username'],
                    email=user['email'] if 'email' in user.keys() else None,
                    google_id=user['google_id'] if 'google_id' in user.keys() else None,
                    profile_photo=user['profile_photo'] if 'profile_photo' in user.keys() else None
                )
        return None

    @staticmethod
    def get_by_email(email):
        with get_db_cursor() as cur:
            cur.execute("SELECT * FROM loggin WHERE email = ?", (email,))
            user = cur.fetchone()
            if user:
                return User(
                    id=user['id'],
                    username=user['username'],
                    email=user['email'],
                    google_id=user['google_id'] if 'google_id' in user.keys() else None,
                    profile_photo=user['profile_photo'] if 'profile_photo' in user.keys() else None
                )
        return None

    
    @staticmethod
    def create(username, email=None, password=None, google_id=None):
        with get_db_cursor() as cur:
            cur.execute(
                "INSERT INTO loggin (username, email, password, google_id) VALUES (?, ?, ?, ?)",
                (username, email, password, google_id)
            )
            return cur.lastrowid