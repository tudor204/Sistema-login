# update_db.py
import sqlite3

def update_database():
    conn = sqlite3.connect('data/loggin.sqlite')
    cursor = conn.cursor()
    
    # Modificar la tabla loggin existente (si es necesario)
    try:
        cursor.execute("ALTER TABLE loggin ADD COLUMN google_id TEXT UNIQUE")
    except sqlite3.OperationalError:
        print("La columna google_id ya existe o no se pudo añadir")
    
    # Crear nuevas tablas
    cursor.executescript("""
    CREATE TABLE IF NOT EXISTS food_entries (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        food_name TEXT NOT NULL,
        calories REAL,
        proteins REAL,
        fats REAL,
        carbs REAL,
        date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES loggin(id)
    );
    
    CREATE TABLE IF NOT EXISTS user_goals (
        user_id INTEGER PRIMARY KEY,
        daily_calories INTEGER DEFAULT 2000,
        daily_proteins INTEGER DEFAULT 50,
        daily_water INTEGER DEFAULT 2,
        FOREIGN KEY (user_id) REFERENCES loggin(id)
    );
    """)
    
    conn.commit()
    conn.close()
    print("✅ Base de datos actualizada exitosamente")

if __name__ == "__main__":
    update_database()