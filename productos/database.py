import sqlite3

def conectar_db():
    conexion = sqlite3.connect("iproducto_db.sqlite")
    return conexion

def inicializar_db():
    try:
        conn = conectar_db()
        cur = conn.cursor()

        # Crear tabla de productos sin el campo de descripción
        cur.execute('''
        CREATE TABLE IF NOT EXISTS productos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            cantidad INTEGER NOT NULL,
            ubicacion TEXT NOT NULL
        )
        ''')

        conn.commit()
        print("productos: Base de datos y tablas creadas correctamente")
        conn.close()
    except Exception as e:
        print(f"productos: Error al inicializar la base de datos: {e}")

def agregar_articulo():
    try:
        conn = conectar_db()
        cur = conn.cursor()

        # Solicitar datos al usuario
        nombre = input("Ingrese el nombre del artículo: ")
        cantidad = int(input("Ingrese la cantidad: "))
        ubicacion = input("Ingrese la ubicación: ")
        
        # Insertar datos en la tabla
        cur.execute('''
        INSERT INTO productos (nombre, cantidad, ubicacion)
        VALUES (?, ?, ?)
        ''', (nombre, cantidad, ubicacion))

        conn.commit()
        print("productos: Artículo agregado correctamente")
        conn.close()
    except Exception as e:
        print(f"productos: Error al agregar el artículo: {e}")

if __name__ == "__main__":
    inicializar_db()
    while True:
        agregar_articulo()
        continuar = input("¿Desea agregar otro artículo? (s/n): ")
        if continuar.lower() != 's':
            break
