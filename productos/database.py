import psycopg2

def conectar_db():
    conexion = psycopg2.connect(
        host="localhost",
        port="5432",
        database="productos_db",
        user="postgres",
        password=""
    )
    return conexion

def probar_conexion():
    try:
        conn = conectar_db()
        print("Productos: Conexion exitosa")
        conn.close()
    except Exception as e:
        print(f"Productos: Error al conectar: {e}")

if __name__ == "__main__":
    probar_conexion()
