import requests
import time
from jwt_auth import generate_token

BASE_URL_PRODUCTOS = "http://localhost:5000"
BASE_URL_INVENTARIO = "http://localhost:5001"

def print_separator():
    print("\n" + "="*50 + "\n")


def test_con_token_valido():
    print("Prueba con token válido:")
    token = generate_token("test_service")
    print(f"Token generado: {token}")
    headers = {"Authorization": token}
    response = requests.get(f"{BASE_URL_PRODUCTOS}/productos", headers=headers)
    print(f"Código de estado: {response.status_code}")
    print(f"Contenido de la respuesta: {response.json()[:2]}...")




if __name__ == "__main__":
    
    print_separator()
    test_con_token_valido()
    print_separator()
    
    
    
    
    
    