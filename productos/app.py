from flask import Flask, request, jsonify
import psycopg2

app = Flask(__name__)

conexion = psycopg2.connect(
    host="localhost",
    port="5432",
    database="productos_db",
    user="postgres",
    password=""
)

@app.route('/productos', methods=['POST'])
def crear_producto():
    data = request.json
    cur = conexion.cursor()
    cur.execute("INSERT INTO productos (nombre, descripcion) VALUES (%s, %s) RETURNING id",
                (data['nombre'], data['descripcion']))
    producto_id = cur.fetchone()[0]
    conexion.commit()
    cur.close()
    return jsonify({"mensaje": "Producto creado", "id": producto_id}), 201

if __name__ == '__main__':
    app.run(port=5000)