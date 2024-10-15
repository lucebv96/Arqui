from flask import Flask, request, jsonify
from database import conectar_db

app = Flask(__name__)

@app.route('/productos', methods=['GET'])
def obtener_productos():
    conn = conectar_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM productos")
    productos = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify([{"id": p[0], "nombre": p[1], "descripcion": p[2]} for p in productos])

@app.route('/productos/<int:id>', methods=['GET'])
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
def crear_producto():
    nuevo_producto = request.json
    conn = conectar_db()
    cur = conn.cursor()
    cur.execute("INSERT INTO productos (nombre, descripcion) VALUES (%s, %s) RETURNING id",
                (nuevo_producto['nombre'], nuevo_producto['descripcion']))
    id_producto = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"id": id_producto, "mensaje": "Producto creado exitosamente"}), 201

@app.route('/productos/<int:id>', methods=['PUT'])
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

@app.route('/productos/<int:id>', methods=['DELETE'])
def eliminar_producto(id):
    conn = conectar_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM productos WHERE id = %s RETURNING id", (id,))
    producto_eliminado = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()
    if producto_eliminado:
        return jsonify({"mensaje": "Producto eliminado exitosamente"})
    return jsonify({"error": "Producto no encontrado"}), 404

if __name__ == '__main__':
    app.run(port=5000, debug=True)