from flask import Flask, request, jsonify
from database import conectar_db
from jwt_auth import token_required
import pika
from resilience import retry_config, cb
from logger import setup_logger

app = Flask(__name__)
logger = setup_logger('productos')

@cb
def publicar_mensaje(mensaje):
    logger.info(f"Intentando publicar mensaje: {mensaje}") 
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        channel = connection.channel()
        channel.queue_declare(queue='productos_queue')
        channel.basic_publish(exchange='', routing_key='productos_queue', body=mensaje)
        connection.close()
        logger.info("Mensaje publicado exitosamente") 
    except Exception as e:
        logger.error(f"Error al publicar mensaje: {str(e)}")
        raise
@app.route('/productos', methods=['GET'])
def obtener_productos():
    conn = conectar_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM productos")
    productos = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify([{"id": p[0], "nombre": p[1], "cantidad": p[2], "ubicacion": p[3]} for p in productos])

@app.route('/productos/<int:id>', methods=['GET'])
def obtener_producto(id):
    conn = conectar_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM productos WHERE id = ?", (id,))
    producto = cur.fetchone()
    cur.close()
    conn.close()
    if producto:
        return jsonify({"id": producto[0], "nombre": producto[1], "cantidad": producto[2], "ubicacion": producto[3]})
    return jsonify({"error": "Producto no encontrado"}), 404

@app.route('/productos', methods=['POST'])
def crear_producto():
    nuevo_producto = request.json
    if not nuevo_producto or 'nombre' not in nuevo_producto or 'cantidad' not in nuevo_producto or 'ubicacion' not in nuevo_producto:
        return jsonify({"error": "Datos de producto inválidos"}), 400
    
    if not nuevo_producto['nombre'].strip() or nuevo_producto['cantidad'] <= 0 or not nuevo_producto['ubicacion'].strip():
        return jsonify({"error": "El nombre no puede estar vacío, la cantidad debe ser mayor a cero, y la ubicación no puede estar vacía"}), 400

    conn = conectar_db()
    cur = conn.cursor()
    try:
        cur.execute("INSERT INTO productos (nombre, cantidad, ubicacion) VALUES (?, ?, ?)", 
                    (nuevo_producto['nombre'], nuevo_producto['cantidad'], nuevo_producto['ubicacion']))
        id_producto = cur.lastrowid
        conn.commit()
        
        # Cambiamos el mensaje para enviar todos los detalles necesarios
        mensaje = f"crear:{id_producto}:{nuevo_producto['nombre']}:{nuevo_producto['cantidad']}:{nuevo_producto['ubicacion']}"
        publicar_mensaje(mensaje)
    except Exception as e:
        conn.rollback()
        logger.error(f"No se pudo publicar el mensaje {id_producto}: {str(e)}")
        return jsonify({"error": "No se pudo crear el producto debido a un error de comunicación"}), 500
    finally:
        cur.close()
        conn.close()

    return jsonify({"id": id_producto, "mensaje": "Producto creado exitosamente"}), 201


@app.route('/productos/<int:id>', methods=['PUT'])
def actualizar_producto(id):
    datos = request.json
    conn = conectar_db()
    cur = conn.cursor()
    try:
        cur.execute("UPDATE productos SET nombre = ?, cantidad = ?, ubicacion = ? WHERE id = ?", 
                    (datos['nombre'], datos['cantidad'], datos['ubicacion'], id))
        if cur.rowcount > 0:
            conn.commit()
            return jsonify({"mensaje": "Producto actualizado exitosamente"})
        else:
            return jsonify({"error": "Producto no encontrado"}), 404
    except Exception as e:
        logger.error(f"Error al actualizar el producto {id}: {str(e)}")
        return jsonify({"error": "No se pudo actualizar el producto debido a un error de comunicación"}), 500
    finally:
        cur.close()
        conn.close()

if __name__ == '__main__':
    logger.info("Iniciando servicio de productos")
    app.run(port=5000, debug=True)
