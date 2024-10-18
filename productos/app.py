from flask import Flask, request, jsonify
from database import conectar_db
from jwt_auth import token_required
import pika
from resilience import retry_config, cb

app = Flask(__name__)

@app.errorhandler(Exception)
def handle_error(error):
    message = str(error)
    status_code = 500
    if isinstance(error, ValueError):
        status_code = 400
    return jsonify({"error": message}), status_code

@retry_config
@cb
def publicar_mensaje(mensaje):
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    channel.queue_declare(queue='productos_queue')
    channel.basic_publish(exchange='', routing_key='productos_queue', body=mensaje)
    connection.close()

@app.route('/productos', methods=['GET'])
@token_required
def obtener_productos():
    conn = conectar_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM productos")
    productos = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify([{"id": p[0], "nombre": p[1], "descripcion": p[2]} for p in productos])

@app.route('/productos/<int:id>', methods=['GET'])
@token_required
def obtener_producto(id):
    conn = conectar_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM productos WHERE id = %s", (id,))
    producto = cur.fetchone()
    cur.close()
    conn.close()
    if producto:
        return jsonify({"id": producto[0], "nombre": producto[1], "descripcion": producto[2]})
    return jsonify({"error": "Producto no encontrado"}), 404

@app.route('/productos', methods=['POST'])
@token_required
def crear_producto():
    try:
        nuevo_producto = request.json
        if not nuevo_producto or 'nombre' not in nuevo_producto or 'descripcion' not in nuevo_producto:
            raise ValueError("Datos de producto inválidos")
        
        conn = conectar_db()
        cur = conn.cursor()
        cur.execute("INSERT INTO productos (nombre, descripcion) VALUES (%s, %s) RETURNING id",
                    (nuevo_producto['nombre'], nuevo_producto['descripcion']))
        id_producto = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()

        publicar_mensaje(f"crear:{id_producto}")

        return jsonify({"id": id_producto, "mensaje": "Producto creado exitosamente"}), 201
    except Exception as e:
        return handle_error(e)

@app.route('/productos/<int:id>', methods=['PUT'])
@token_required
def actualizar_producto(id):
    datos = request.json
    conn = conectar_db()
    cur = conn.cursor()
    cur.execute("UPDATE productos SET nombre = %s, descripcion = %s WHERE id = %s RETURNING id",
                (datos['nombre'], datos['descripcion'], id))
    producto_actualizado = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()
    if producto_actualizado:
        return jsonify({"mensaje": "Producto actualizado exitosamente"})
    return jsonify({"error": "Producto no encontrado"}), 404

if __name__ == '__main__':
    app.run(port=5000, debug=True)