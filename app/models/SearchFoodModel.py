from app.conexion import get_db_cursor
import datetime

def save_food_entry(user_id, food_name, calories, proteins, fats, carbs):
    """
    Guarda una entrada de comida para un usuario en la base de datos
    y actualiza los totales consumidos en la tabla de objetivos del usuario.

    """
    current_date = datetime.date.today().strftime('%Y-%m-%d')
    current_timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') # Obtener timestamp actual
    try:
        with get_db_cursor() as cursor:
            # 1. Insertar el registro de comida en food_entries
            # ¡Ahora incluyendo 'created_at' en la lista de columnas y valores!
            cursor.execute('''
                INSERT INTO food_entries 
                (user_id, food_name, calories, proteins, fats, carbs, date, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (user_id, food_name, calories, proteins, fats, carbs, current_date, current_timestamp))

            # 2. Actualizar los valores consumidos en user_goals
            cursor.execute('''
                UPDATE user_goals 
                SET calories_consumed = IFNULL(calories_consumed, 0) + ?,
                    proteins_consumed = IFNULL(proteins_consumed, 0) + ?,
                    fats_consumed = IFNULL(fats_consumed, 0) + ?,
                    carbs_consumed = IFNULL(carbs_consumed, 0) + ?,
                    updated_at = ?
                WHERE user_id = ?
            ''', (calories, proteins, fats, carbs, datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), user_id))

    except Exception as e:
        print(f"Error en save_food_entry: {e}")
        raise

def calculate_macros_for_quantity(original_calories, original_proteins, original_fats, original_carbs, quantity_g):
    """
    Calcula los macros para una cantidad dada, basándose en los valores por 100g.
    """
    if quantity_g <= 0:
        return 0, 0, 0, 0

    factor = quantity_g / 100.0
    
    cal = (float(original_calories) * factor) if str(original_calories).replace('.', '', 1).isdigit() else 0
    prot = (float(original_proteins) * factor) if str(original_proteins).replace('.', '', 1).isdigit() else 0
    fat = (float(original_fats) * factor) if str(original_fats).replace('.', '', 1).isdigit() else 0
    carb = (float(original_carbs) * factor) if str(original_carbs).replace('.', '', 1).isdigit() else 0

    return round(cal, 2), round(prot, 2), round(fat, 2), round(carb, 2)

def get_food_entries_for_date(user_id, target_date=None):
    """
    Obtiene todas las entradas de comida de un usuario en una fecha específica.
    :param user_id: ID del usuario
    :param target_date: fecha (YYYY-MM-DD). Si es None, se usa hoy.
    :return: lista de diccionarios con los campos de la comida
    """
    if target_date is None:
        target_date = datetime.date.today().strftime('%Y-%m-%d')

    try:
        with get_db_cursor() as cursor:
            cursor.execute('''
                SELECT food_name, calories, proteins, fats, carbs, created_at
                FROM food_entries
                WHERE user_id = ? AND date = ?
                ORDER BY created_at DESC
            ''', (user_id, target_date))
            
            rows = cursor.fetchall()
            # Convertir a lista de diccionarios
            alimentos = [{
                "nombre": row[0],
                "calorias": row[1],
                "proteinas": row[2],
                "grasas": row[3],
                "carbohidratos": row[4],
                "hora": row[5]
            } for row in rows]

            return alimentos

    except Exception as e:
        print(f"Error en get_food_entries_for_date: {e}")
        return []


