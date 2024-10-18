import sqlite3

# Conectar a una base de datos SQLite
def conectar_db():
    conexion = sqlite3.connect('inventario.db')  # Nombre del archivo SQLite
    return conexion

# Probar la conexión
def probar_conexion():
    try:
        conn = conectar_db()
        print("Inventario: Conexión a SQLite exitosa")
        conn.close()
    except Exception as e:
        print(f"Inventario: Error al conectar a SQLite: {e}")

if __name__ == "__main__":
    probar_conexion()
