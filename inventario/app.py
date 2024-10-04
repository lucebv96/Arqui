from flask import Flask, request, jsonify
import psycopg2

app = Flask(__name__)

conexion = psycopg2.connect(
    host="localhost",
    port="5432",
    database="inventario_db",
    user="postgres",
    password=""
)

@app.route('/inventario/<int:producto_id>', methods=['GET'])
def obtener_inventario(producto_id):
    cur = conexion.cursor()
    cur.execute("SELECT cantidad FROM inventario WHERE producto_id = %s", (producto_id,))
    resultado = cur.fetchone()
    cur.close()
    if resultado:
        return jsonify({"producto_id": producto_id, "cantidad": resultado[0]}), 200
    else:
        return jsonify({"mensaje": "Producto no encontrado"}), 404

if __name__ == '__main__':
    app.run(port=5001)