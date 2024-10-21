import requests
import time
from inventario.jwt_auth import generate_token


BASE_URL_PRODUCTOS = "http://localhost:5000"
BASE_URL_INVENTARIO = "http://localhost:5001"

def print_separator():
    print("\n" + "="*50 + "\n")

def test_sin_token():
    print("Prueba sin token:")
    response = requests.get(f"{BASE_URL_PRODUCTOS}/productos")
    print(f"Respuesta: {response.status_code}, {response.json()}")

def test_con_token_valido():
    print("Prueba con token válido:")
    token = generate_token("test_service")
    print(f"Token generado: {token}")
    headers = {"Authorization": token}
    response = requests.get(f"{BASE_URL_PRODUCTOS}/productos", headers=headers)
    print(f"Código de estado: {response.status_code}")
    print(f"Contenido de la respuesta: {response.json()[:2]}...")

def test_comunicacion_asincrona():
    print("Prueba de comunicación asíncrona:")
    token = generate_token("test_service")
    headers = {"Authorization": token}
    
    nuevo_producto = {"nombre": "Producto Asíncrono", "descripcion": "Prueba de mensajería"}
    response = requests.post(f"{BASE_URL_PRODUCTOS}/productos", headers=headers, json=nuevo_producto)
    if response.status_code == 201:
        print("Producto creado exitosamente")
        producto_id = response.json()["id"]
        
        time.sleep(2)
        
        response = requests.get(f"{BASE_URL_INVENTARIO}/inventario/{producto_id}", headers=headers)
        if response.status_code == 200:
            print(f"Inventario creado para el producto {producto_id}")
        else:
            print("Error: No se encontró el inventario para el nuevo producto")
    else:
        print("Error al crear el producto")

def test_actualizar_inventario():
    print("Prueba de actualización de inventario:")
    token = generate_token("test_service")
    headers = {"Authorization": token}
    
    # Crear un nuevo producto
    nuevo_producto = {"nombre": "Producto Test", "descripcion": "Prueba de actualización de inventario"}
    response = requests.post(f"{BASE_URL_PRODUCTOS}/productos", headers=headers, json=nuevo_producto)
    if response.status_code == 201:
        producto_id = response.json()["id"]
        print(f"Producto creado con ID: {producto_id}")
        
        time.sleep(2)  # Esperar a que se procese el mensaje asíncrono
        
        # Actualizar el inventario
        nueva_cantidad = 10
        response = requests.put(f"{BASE_URL_INVENTARIO}/inventario/{producto_id}", 
                                headers=headers, 
                                json={"cantidad": nueva_cantidad})
        if response.status_code == 200:
            print(f"Inventario actualizado exitosamente para el producto {producto_id}")
        else:
            print(f"Error al actualizar el inventario: {response.json()}")
        
        # Verificar la actualización
        response = requests.get(f"{BASE_URL_INVENTARIO}/inventario/{producto_id}", headers=headers)
        if response.status_code == 200:
            print(f"Inventario actual: {response.json()}")
        else:
            print("Error al obtener el inventario actualizado")
    else:
        print("Error al crear el producto para la prueba de inventario")

if __name__ == "__main__":
    test_sin_token()
    print_separator()
    test_con_token_valido()
    print_separator()
    test_comunicacion_asincrona()
    print_separator()
    test_actualizar_inventario()
