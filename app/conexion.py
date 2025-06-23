import sqlite3
ORIGIN_DATA = "data/loggin.sqlite"

class Conexion:
    def __init__(self, query_sql, params=()):
        self.con = sqlite3.connect(ORIGIN_DATA)
        self.cur = self.con.cursor()
        try:
            self.res = self.cur.execute(query_sql, params)
            self.con.commit()
        except sqlite3.Error as e:
            self.con.rollback()
            raise e

    def fetch_all(self):
        columns = [desc[0] for desc in self.res.description]
        return [dict(zip(columns, row)) for row in self.res.fetchall()]

    def close(self):
        self.con.close()