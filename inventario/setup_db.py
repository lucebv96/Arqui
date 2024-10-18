import sqlite3

def inicializar_bd():
    conn = sqlite3.connect('inventario.db')
    cursor = conn.cursor()
    
    # Crear tabla inventario
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS inventario (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            producto_id INTEGER,
            cantidad INTEGER
        )
    ''')
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    inicializar_bd()
    print("Base de datos SQLite inicializada.")
