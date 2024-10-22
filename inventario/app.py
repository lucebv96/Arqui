from flask import Flask, request, jsonify
from database import conectar_db
from jwt_auth import token_required
import pika
from resilience import retry_config, cb
from logger import setup_logger

app = Flask(__name__)
logger = setup_logger('inventario')

@retry_config
@cb
def publicar_mensaje(mensaje):
    logger.info(f"Intentando publicar mensaje: {mensaje}")
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        channel = connection.channel()
        channel.queue_declare(queue='inventario_queue')
        channel.basic_publish(exchange='', routing_key='inventario_queue', body=mensaje)
        connection.close()
        logger.info("Mensaje publicado exitosamente")
    except Exception as e:
        logger.error(f"Error al publicar mensaje: {str(e)}")
        raise

@app.route('/inventario', methods=['GET'])
@token_required
def obtener_inventario():
    conn = conectar_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM inventario")
    inventario = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify([{"id": i[0], "nombre": i[1], "cantidad": i[2], "ubicacion": i[3]} for i in inventario])

@app.route('/inventario/<int:id>', methods=['GET'])
@token_required
def obtener_item_inventario(id):
    conn = conectar_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM inventario WHERE id = ?", (id,))
    item = cur.fetchone()
    cur.close()
    conn.close()
    if item:
        return jsonify({"id": item[0], "nombre": item[1], "cantidad": item[2], "ubicacion": item[3]})
    return jsonify({"error": "Item no encontrado"}), 404

@app.route('/inventario', methods=['POST'])
@token_required
def crear_item_inventario():
    nuevo_item = request.json
    if not nuevo_item or 'nombre' not in nuevo_item or 'cantidad' not in nuevo_item:
        return jsonify({"error": "Datos de inventario inválidos"}), 400

    if not nuevo_item['nombre'].strip() or not str(nuevo_item['cantidad']).isdigit():
        return jsonify({"error": "Nombre o cantidad inválidos"}), 400

    conn = conectar_db()
    cur = conn.cursor()
    cur.execute("INSERT INTO inventario (nombre, cantidad, ubicacion) VALUES (?, ?, ?)",
                (nuevo_item['nombre'], nuevo_item['cantidad'], nuevo_item.get('ubicacion')))
    id_item = cur.lastrowid

    try:
        publicar_mensaje(f"crear:{id_item}")
    except Exception as e:
        conn.rollback()
        logger.error(f"No se pudo publicar el mensaje {id_item}")
        return jsonify({"error": "No se pudo crear el item de inventario debido a un error de comunicación"}), 500

    conn.commit()
    return jsonify({"id": id_item, "mensaje": "Item creado exitosamente"}), 201
    cur.close()
    conn.close()

@app.route('/inventario/<int:id>', methods=['PUT'])
@token_required
def actualizar_item_inventario(id):
    datos = request.json
    conn = conectar_db()
    cur = conn.cursor()
    cur.execute("UPDATE inventario SET nombre = ?, cantidad = ?, ubicacion = ? WHERE id = ?",
                (datos['nombre'], datos['cantidad'], datos.get('ubicacion'), id))
    item_actualizado = cur.rowcount
    conn.commit()
    cur.close()
    conn.close()
    if item_actualizado:
        return jsonify({"mensaje": "Item actualizado exitosamente"})
    return jsonify({"error": "Item no encontrado"}), 404

if __name__ == '__main__':
    logger.info("Iniciando servicio de inventario")
    app.run(port=5001, debug=True)
