import sqlite3

def conectar_db():
    conexion = sqlite3.connect("inventario_db.sqlite")
    return conexion

def inicializar_db():
    conn = None
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
    except Exception as e:
        print(f"Inventario: Error al inicializar la base de datos: {e}")
    finally:
        
        if conn:
            conn.close()

def agregar_articulo():
    conn = None
    try:
        conn = conectar_db()
        cur = conn.cursor()

        # Solicitar datos al usuario
        nombre = input("Ingrese el nombre del artículo: ")
        cantidad = int(input("Ingrese la cantidad: "))
        ubicacion = input("Ingrese la ubicación: ")

        # Insertar datos en la tabla
        cur.execute('''
        INSERT INTO inventario (nombre, cantidad, ubicacion)
        VALUES (?, ?, ?)
        ''', (nombre, cantidad, ubicacion))

        conn.commit()
        print("Inventario: Artículo agregado correctamente")
    except Exception as e:
        print(f"Inventario: Error al agregar el artículo: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    inicializar_db()
    while True:
        agregar_articulo()
        continuar = input("¿Desea agregar otro artículo? (s/n): ")
        if continuar.lower() != 's':
            break
