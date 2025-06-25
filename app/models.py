from flask_login import UserMixin
from app.conexion import Conexion

class User(UserMixin):
    def __init__(self, id, username, email):
        self.id = id
        self.username = username
        self.email = email

    @staticmethod
    def get_by_id(user_id):
        query = "SELECT id, username, email FROM loggin WHERE id = ?"
        con = Conexion(query, (user_id,))
        row = con.res.fetchone()
        con.close()
        if row:
            return User(id=row[0], username=row[1], email=row[2])
        return None

    @staticmethod
    def get_by_email(email):
        query = "SELECT id, username, email FROM loggin WHERE email = ?"
        con = Conexion(query, (email,))
        row = con.res.fetchone()
        con.close()
        if row:
            return User(id=row[0], username=row[1], email=row[2])
        return None

    @staticmethod
    def create(username, email):
        # Si no tienes la columna email en la tabla loggin, deberás añadirla o adaptar
        insert_query = "INSERT INTO loggin (username, email) VALUES (?, ?)"
        con = Conexion(insert_query, (username, email))
        con.close()
