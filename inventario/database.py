import sqlite3

def conectar_db():
    conexion = sqlite3.connect("inventario_db.sqlite")
    return conexion

def inicializar_db():
    try:
        conn = conectar_db()
        cur = conn.cursor()

        # Crear tabla de inventario
        cur.execute('''
        CREATE TABLE IF NOT EXISTS inventario (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            cantidad INTEGER NOT NULL,
            ubicacion TEXT
        )
        ''')

        conn.commit()
        print("Inventario: Base de datos y tablas creadas correctamente")
        conn.close()
    except Exception as e:
        print(f"Inventario: Error al inicializar la base de datos: {e}")

if __name__ == "__main__":
    inicializar_db()
