from flask import Flask, request, jsonify
from database import conectar_db

app = Flask(__name__)

@app.route('/inventario', methods=['GET'])
def obtener_inventario():
    conn = conectar_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM inventario")
    inventario = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify([{"producto_id": i[0], "cantidad": i[1]} for i in inventario])

@app.route('/inventario/<int:producto_id>', methods=['GET'])
def obtener_inventario_producto(producto_id):
    conn = conectar_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM inventario WHERE producto_id = %s", (producto_id,))
    item = cur.fetchone()
    cur.close()
    conn.close()
    if item:
        return jsonify({"producto_id": item[0], "cantidad": item[1]})
    return jsonify({"error": "Producto no encontrado en inventario"}), 404

@app.route('/inventario/<int:producto_id>', methods=['PUT'])
def actualizar_inventario(producto_id):
    datos = request.json
    conn = conectar_db()
    cur = conn.cursor()
    cur.execute("UPDATE inventario SET cantidad = %s WHERE producto_id = %s RETURNING producto_id, cantidad",
                (datos['cantidad'], producto_id))
    resultado = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()
    if resultado:
        return jsonify({"producto_id": resultado[0], "cantidad": resultado[1], "mensaje": "Inventario actualizado exitosamente"}), 200
    return jsonify({"error": "Producto no encontrado en inventario"}), 404

# Endpoint temporal para probar 
@app.route('/inventario/prueba', methods=['POST'])
def crear_inventario_desarrollo():
    datos = request.json
    conn = conectar_db()
    cur = conn.cursor()
    cur.execute("INSERT INTO inventario (producto_id, cantidad) VALUES (%s, %s) ON CONFLICT (producto_id) DO UPDATE SET cantidad = EXCLUDED.cantidad RETURNING producto_id, cantidad",
                (datos['producto_id'], datos['cantidad']))
    resultado = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"producto_id": resultado[0], "cantidad": resultado[1], "mensaje": "Registro de inventario creado/actualizado"}), 201

if __name__ == '__main__':
    app.run(port=5001, debug=True)